# Generated by Django 4.1.7 on 2023-04-09 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Billing', '0006_customer_birth_date_alter_customer_order_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='district',
            field=models.CharField(default='-', max_length=100),
        ),
        migrations.AlterField(
            model_name='customer',
            name='order_type',
            field=models.CharField(choices=[('super market', 'Super Market'), ('franchise', 'Franchise'), ('normal', 'Normal Customer'), ('exhibition', 'Exhibition')], default='normal', max_length=30),
        ),
    ]
