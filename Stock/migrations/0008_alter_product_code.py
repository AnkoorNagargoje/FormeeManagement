# Generated by Django 4.1.7 on 2023-03-23 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stock', '0007_product_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='code',
            field=models.CharField(max_length=4, unique=True),
        ),
    ]
