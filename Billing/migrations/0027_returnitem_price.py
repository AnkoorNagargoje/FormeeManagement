# Generated by Django 4.1.7 on 2024-04-12 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Billing', '0026_orderitem_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='returnitem',
            name='price',
            field=models.FloatField(default=0),
        ),
    ]
