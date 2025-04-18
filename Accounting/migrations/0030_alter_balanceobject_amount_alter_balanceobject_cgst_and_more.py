# Generated by Django 4.1.7 on 2023-07-31 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounting', '0029_balance_alter_subdebit_cgst_alter_subdebit_sgst_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balanceobject',
            name='amount',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='balanceobject',
            name='cgst',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='balanceobject',
            name='sgst',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='balanceobject',
            name='sub_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='subdebit',
            name='cgst',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='subdebit',
            name='sgst',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]
