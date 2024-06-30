from uuid import uuid4

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import UniqueConstraint, Q
from django.db.models.functions import Lower
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django_lifecycle import LifecycleModelMixin, hook, BEFORE_UPDATE, AFTER_UPDATE

from core.model_field import IPv4AddressIntegerField, BooleanYNField


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # 최초 생성시각을 자동 저장
    updated_at = models.DateTimeField(auto_now=True)  # 매 수정시각을 자동 저장

    class Meta:
        abstract = True


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Post.Status.PUBLISHED)

    def draft(self):
        return self.filter(status=Post.Status.DRAFT)

    def search(self, query: str):
        return self.filter(title__contains=query)

    def create(self, **kwargs):
        kwargs.setdefault("status", Post.Status.PUBLISHED)
        return super().create(**kwargs)


class Post(LifecycleModelMixin, models.Model):
    class Status(models.TextChoices):  # 문자열 선택지
        DRAFT = "D", "초안"  # 상수, 값, 레이블
        PUBLISHED = "P", "발행"

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_post_set",
        related_query_name="blog_post",
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(
        max_length=120,
        allow_unicode=True,
        help_text="title 필드로 부터 자동생성합니다.",
    )
    status = models.CharField(
        # 선택지 값 크기에 맞춰 최대 길이를 지정
        max_length=1,
        # choices 속성으로 사용할 수 있도록 2중 리스트로 반환
        # choices 속성은 모든 모델 필드에서 지원합니다.
        choices=Status.choices,
        # status 필드에 대한 모든 값 지정에는 상수로 지정하면 쿼리에 값으로 자동 변환
        default=Status.DRAFT,
    )
    content = models.TextField()
    tag_set = models.ManyToManyField(
        "Tag",
        blank=True,
        related_name="blog_post_set",
        related_query_name="blog_post",
        through="PostTagRelation",
        through_fields=("post", "tag"),
    )

    objects = PostQuerySet.as_manager()

    created_at = models.DateTimeField(auto_now_add=True)  # 최초 생성시각을 자동 저장
    updated_at = models.DateTimeField(auto_now_add=True)

    def slugify(self, force=False):
        if force or not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
            self.slug = self.slug[:112]
            # 제목으로 만든 slug 문자열 뒤에 uuid 를 붙여 slug 의 유일성을 확보
            self.slug += "-" + uuid4().hex[:8]

    # def save(self, *args, **kwargs):
    #     # save 시에 slug 필드를 자동으로 채워줌
    #     self.slugify()
    #     super().save(*args, **kwargs

    @hook(BEFORE_UPDATE, when="content", has_changed=True)
    def on_changed_content(self):
        print("content 필드 변경으로, updated_at 을 갱신합니다. ")
        self.updated_at = timezone.now()

    @hook(AFTER_UPDATE, when="status", was=Status.DRAFT, is_now=Status.PUBLISHED)
    def on_published(self):
        print("저자에게 이메일을 보냅니다.")

    class Meta:
        # unique=True 보다 강력한 Unique 제약사항 추가 방법
        constraints = [UniqueConstraint("slug", name="unique_slug")]
        verbose_name = "포스팅"
        verbose_name_plural = "포스팅 목록"
        permissions = [("view_premium_post", "프리미엄 블로그를 볼 수 있음")]

    def __str__(self):
        # choices 속성을 사용한 필드는 get_필드명_display() 함수를 통해 레이블 조회를 지원합니다.
        return f"{self.title} ({self.get_status_display()})"


@receiver(pre_save, sender=Post)
def pre_save_on_save(sender, instance: Post, **kwargs):
    print("pre_save_on_save 호출")
    instance.slugify()


class Comment(TimestampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()


class AccessLog(TimestampedModel):
    ip_generic = models.GenericIPAddressField(protocol="IPv4")
    ip_int = IPv4AddressIntegerField()


class Article(TimestampedModel):
    title = models.CharField(max_length=100)
    is_public_ch = models.CharField(
        max_length=1,
        choices=[
            ("Y", "예"),
            ("N", "아니오"),
        ],
        default="N",
    )
    is_public_yn = BooleanYNField(default=False)


class Review(TimestampedModel, models.Model):
    message = models.TextField()
    rating = models.SmallIntegerField(
        # validators=[
        #     MinValueValidator(1),
        #     MaxValueValidator(5),
        # ]
    )

    def get_absolute_url(self) -> str:
        return reverse("blog:review_detail", args=[self.pk])

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(rating__gte=1, rating__lte=5),
                name="blog_review_rating_gte_1_lte_5",
            )
        ]
        db_table_comment = "사용자 리뷰와 평점을 저장하는 테이블. 평점(rating)은 1에서 5사이의 값으로 제한."


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                # fields=["name"],
                Lower("name"),
                name="blog_tag_name_unique",
            )
        ]
        indexes = [
            # models.Index(fields=["name"]),
            models.Index(
                fields=["name"],
                name="blog_tag_name_like",
                opclasses=["varchar_pattern_ops"],
            )
        ]


class PostTagRelation(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "tag"],
                name="blog_post_tag_relation_unique",
            )
        ]


class Student(models.Model):
    name = models.CharField(max_length=100)


class Course(models.Model):
    title = models.CharField(max_length=100)


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                "student", "course", Lower("semester"), name="blog_enrollment_uniq"
            )
        ]


class Memo(models.Model):
    class Status(models.TextChoices):
        PRIVATE = "V", "비공개"
        PUBLIC = "P", "공개"

    message = models.CharField(max_length=140)
    status = models.CharField(
        max_length=1, default=Status.PUBLIC, choices=Status.choices
    )
    created_at = models.DateTimeField(auto_now_add=True)
