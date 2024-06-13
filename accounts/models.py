from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    address = models.CharField(max_length=100, blank=True)
    point = models.PositiveIntegerField(default=0)
