# Generated by Django 4.1.7 on 2024-05-02 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Billing', '0027_returnitem_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='invoice_number',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
