# Generated by Django 4.1.7 on 2023-06-07 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounting', '0020_remove_debit_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debit',
            name='amount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='subdebit',
            name='amount',
            field=models.FloatField(),
        ),
    ]
