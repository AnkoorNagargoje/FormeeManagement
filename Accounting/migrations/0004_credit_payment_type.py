# Generated by Django 4.1.7 on 2023-04-14 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounting', '0003_credit_date_credit_transaction_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='credit',
            name='payment_type',
            field=models.CharField(default='Cash', max_length=20),
        ),
    ]
