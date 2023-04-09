from django.db import models
from Billing.models import Order
import datetime


class Credit(models.Model):
    name = models.CharField(max_length=200)
    amount = models.FloatField()
    invoice_number = models.PositiveIntegerField(blank=True, null=True)
    transaction_number = models.PositiveBigIntegerField(default=0)
    date = models.DateField(default=datetime.date.today)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            order = Order.objects.get(id=self.invoice_number)
            order.payment_status = 'Paid'
            order.save()
        except Order.DoesNotExist:
            pass


class Debit(models.Model):
    name = models.CharField(max_length=200)
    amount = models.FloatField()
    reason = models.CharField(max_length=200)