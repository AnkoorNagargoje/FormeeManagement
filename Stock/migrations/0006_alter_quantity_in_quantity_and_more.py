# Generated by Django 4.1.7 on 2023-03-23 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stock', '0005_alter_quantity_in_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quantity',
            name='in_quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='quantity',
            name='out_quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
