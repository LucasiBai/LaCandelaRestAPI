# Generated by Django 4.1 on 2022-11-24 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("db", "0002_historicaluseraccount"),
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
                ("title", models.CharField(max_length=255, unique=True)),
            ],
        ),
    ]