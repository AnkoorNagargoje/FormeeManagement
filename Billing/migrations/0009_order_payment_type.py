# Generated by Django 4.1.7 on 2023-04-15 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Billing', '0008_order_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_type',
            field=models.CharField(default='Cash', max_length=20),
        ),
    ]
