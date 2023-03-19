# Generated by Django 4.1 on 2023-03-02 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0011_shippinginfo_is_selected'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippinginfo',
            name='ship_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
    ]