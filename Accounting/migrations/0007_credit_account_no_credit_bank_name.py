# Generated by Django 4.1.7 on 2023-05-20 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounting', '0006_alter_credit_transaction_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='credit',
            name='account_no',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='credit',
            name='bank_name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
