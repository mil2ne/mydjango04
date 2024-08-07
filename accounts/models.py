import datetime

from django.contrib.auth.models import AbstractUser, Permission, Group
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from core.model_field import DatePickerField


def group_add_perm(self, perm_name: str) -> None:
    group = self
    app_label, codename = perm_name.split(".", maxsplit=1)
    permission = Permission.objects.get(
        content_type__app_label=app_label,
        codename=codename,
    )
    group.permissions.add(permission)


setattr(Group, "add_perm", group_add_perm)


class User(AbstractUser):
    friend_set = models.ManyToManyField(
        to="self", blank=True, symmetrical=True, related_query_name="friend_user"
    )

    follower_set = models.ManyToManyField(
        to="self",
        blank=True,
        symmetrical=False,
        related_name="following_set",
        related_query_name="following",
    )

    def add_perm(self, perm_name: str) -> None:
        user = self
        app_label, codename = perm_name.split(".", maxsplit=1)

        permission = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )
        user.user_permissions.add(permission)


class SuperUserManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_superuser=True)


@receiver(post_save, sender=User)
def post_save_on_user(instance: User, created: bool, **kwargs):
    if created:
        print(f"user({instance}) 생성!!!")
        Profile.objects.create(user=instance)


class SuperUser(User):
    objects = SuperUserManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.is_superuser = True
        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        related_query_name="profile",
    )
    birth_date = DatePickerField(
        min_value=lambda: datetime.date.today(),
        max_value=lambda: datetime.date.today() + datetime.timedelta(days=7),
        blank=True,
        null=True,
    )
    address = models.CharField(max_length=100, blank=True)
    location_point = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(
        max_length=13,
        blank=True,
        validators=[
            RegexValidator(
                r"^01\d[ -]?\d{4}[ -]?\d{4}$",
                message="휴대폰 번호 포맷으로 입력하세요.",
            )
        ],
    )
    point = models.PositiveIntegerField(default=0)

    photo = models.ImageField(upload_to="profile/photo", blank=True)


@receiver(post_delete, sender=Profile)
def post_delete_in_profile(instance: Profile, **kwargs):
    instance.photo.delete(save=False)
