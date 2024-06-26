# Generated by Django 4.2.13 on 2024-06-06 16:28

from django.db import migrations, models
import django.db.models.deletion


def create_initial_category(apps, schema_editor):
    # 최소 1개의 category 가 있도록 생성
    Category = apps.get_model("blog", "Category")

    is_existed = Category.objects.filter(pk=1).exists()
    if is_existed is False:
        Category.objects.create(name="initial", pk=1)


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0003_post_author"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.RunPython(
            create_initial_category,
            migrations.RunPython.noop,
        ),
        migrations.AddField(
            model_name="post",
            name="category",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="blog.category",
            ),
            preserve_default=False,
        ),
    ]
