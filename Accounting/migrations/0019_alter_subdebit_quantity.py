# Generated by Django 4.1.7 on 2023-06-07 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounting', '0018_alter_subdebit_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subdebit',
            name='quantity',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
