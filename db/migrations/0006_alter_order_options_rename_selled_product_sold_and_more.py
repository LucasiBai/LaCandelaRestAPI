# Generated by Django 4.1 on 2022-12-06 13:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("db", "0005_alter_product_images_shippinginfo_order"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="order",
            options={"verbose_name": "Order", "verbose_name_plural": "Orders"},
        ),
        migrations.RenameField(
            model_name="product",
            old_name="selled",
            new_name="sold",
        ),
        migrations.AlterField(
            model_name="order",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("9224ecd6-0ff9-4454-bd3e-6d5e9e2c2d82"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]