# Generated by Django 4.1.7 on 2023-06-02 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stock', '0015_product_barcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='barcode',
            field=models.BigIntegerField(default=0),
        ),
    ]
