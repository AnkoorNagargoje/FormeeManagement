# Generated by Django 4.1.7 on 2023-04-16 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Billing', '0010_alter_order_payment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='district',
            field=models.CharField(default='', max_length=100),
        ),
    ]
