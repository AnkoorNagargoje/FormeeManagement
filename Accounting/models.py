from django.db import models
from Billing.models import Order


class Credit(models.Model):
    name = models.CharField(max_length=200)
    amount = models.FloatField()
    invoice_number = models.PositiveIntegerField(blank=True, null=True)

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