from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse


# Create your models here.
class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = (
            "D",
            "초안",
        )
        PUBLISHED = "P", "발행"

    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    status = models.CharField(
        max_length=1, choices=Status.choices, default=Status.DRAFT
    )

    photo = models.ImageField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    ip = models.GenericIPAddressField()
    comment_set = GenericRelation("Comment", related_query_name="post")

    tag_set = models.ManyToManyField(
        "blog.Tag",
        blank=True,
        related_name="weblog_post_set",
        related_query_name="weblog_post",
    )

    def get_absolute_url(self) -> str:
        return reverse("weblog:post_detail", args=[self.pk])


@receiver(pre_delete, sender=Post)
def set_value_or_delete(sender, instance: Post, **kwargs):
    instance.comment_set.update(object_id=5)


class Article(models.Model):
    title = models.CharField(max_length=100)
    comment_set = GenericRelation("Comment", related_query_name="article")


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_id")
    message = models.TextField()
    rating = models.SmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )
