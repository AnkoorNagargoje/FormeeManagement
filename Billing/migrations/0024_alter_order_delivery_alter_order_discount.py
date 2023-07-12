# Generated by Django 4.1.7 on 2023-07-12 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Billing', '0023_returnitem_payment_status_returnitem_payment_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='discount',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
