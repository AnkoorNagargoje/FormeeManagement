# Generated by Django 4.1.7 on 2025-01-15 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Billing', '0031_orderitem_batchno'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='batchno',
            field=models.CharField(default='', max_length=20),
        ),
    ]
