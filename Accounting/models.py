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
TYPE = (
    ('purchase', 'Purchase'),
    ('indirect', 'Indirect'),
    ('fixed', 'Fixed'),
    ('miscellaneous', 'Miscellaneous'),
)


class Debit(models.Model):
    name = models.CharField(max_length=200)
    amount = models.FloatField()
    reason = models.CharField(max_length=200)
    person = models.CharField(max_length=200, default='')
    how = models.CharField(max_length=20, choices=HOW_CHOICES, default='self')
    date = models.DateTimeField(auto_now_add=False, editable=True, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE, default='miscellaneous')


class DebitOrder(models.Model):
    debit = models.ForeignKey(Debit, on_delete=models.CASCADE, related_name='debit_orders')
    type = models.CharField(max_length=100)
    amount = models.FloatField()


class DebitItem(models.Model):
    debit_order = models.ForeignKey(DebitOrder, on_delete=models.CASCADE, related_name='debit_items')
    amount = models.FloatField()
    item = models.ForeignKey('Item', on_delete=models.CASCADE)


class Item(models.Model):
    name = models.CharField(max_length=100, default='')