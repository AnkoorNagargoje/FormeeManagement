# Generated by Django 4.1.7 on 2025-01-15 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Billing', '0030_order_payment_terms'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='batchno',
            field=models.IntegerField(default=0),
        ),
    ]
