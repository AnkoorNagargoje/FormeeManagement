# Generated by Django 4.1.7 on 2023-06-20 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounting', '0022_subdebit_cgst_subdebit_sgst'),
    ]

    operations = [
        migrations.AddField(
            model_name='subdebit',
            name='sub_amount',
            field=models.FloatField(default=0),
        ),
    ]
