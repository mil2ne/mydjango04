# Generated by Django 4.2.13 on 2024-06-08 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0009_review_alter_post_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
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
                ("name", models.CharField(max_length=100)),
            ],
        ),
    ]
