# Generated by Django 4.1.7 on 2023-07-22 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounting', '0025_alter_subdebit_price_alter_subdebit_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debittype',
            name='type',
            field=models.CharField(choices=[('purchase', 'Purchase'), ('direct', 'Direct'), ('indirect', 'Indirect'), ('miscellaneous', 'Miscellaneous')], max_length=15),
        ),
    ]
