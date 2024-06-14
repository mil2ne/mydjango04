from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    comment_set = GenericRelation("Comment", related_query_name="post")


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