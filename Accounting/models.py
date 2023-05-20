from django.db import models
from Billing.models import Order
import datetime


class Credit(models.Model):
    name = models.CharField(max_length=200)
    amount = models.FloatField()
    invoice_number = models.PositiveIntegerField(blank=True, null=True)
    payment_type = models.CharField(max_length=20, default='Cash')
    transaction_number = models.PositiveBigIntegerField(default=0, null=True, blank=True)
    date = models.DateField(default=datetime.date.today)
    account_no = models.CharField(max_length=100, default="")
    bank_name = models.CharField(max_length=100, default="")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            order = Order.objects.get(id=self.invoice_number)
            order.payment_status = 'Paid'
            order.save()
        except Order.DoesNotExist:
            pass


HOW_CHOICES = (
    ('self', 'Self'),
    ('bank', 'Bank'),
    ('shop', 'Shop Cash'),
)


class Debit(models.Model):
    name = models.CharField(max_length=200)
    amount = models.FloatField()
    reason = models.CharField(max_length=200)
    person = models.CharField(max_length=200, default='')
    how = models.CharField(max_length=20, choices=HOW_CHOICES, default='self')
