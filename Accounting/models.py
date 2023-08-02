from django.db import models
from Billing.models import Order
import datetime
from django.db.models import Sum


CREDIT_TYPE = (
    ('sales', 'Sales'),
    ('indirect', 'Indirect'),
    ('miscellaneous', 'Miscellaneous'),
)


class Credit(models.Model):
    name = models.CharField(max_length=200)
    amount = models.FloatField()
    invoice_number = models.PositiveIntegerField(blank=True, null=True)
    payment_type = models.CharField(max_length=20, default='Cash')
    transaction_number = models.PositiveBigIntegerField(default=0, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=False, editable=True, null=True)
    cheque_no = models.CharField(max_length=100, default="")
    bank_name = models.CharField(max_length=100, default="")
    note = models.CharField(max_length=100, default='')
    credit_type = models.CharField(max_length=20, choices=CREDIT_TYPE, default='sales')

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
    ('material purchase', 'Material Purchase'),
    ('fuel', 'Fuel Consumption'),
    ('wastage', 'Process Wastage'),
    ('labour', 'Labour Expenses'),
    ('freight', 'Freight and Carriage'),
    ('production overhead', 'Production Overhead'),
    ('utilities', 'Utilities'),
    ('maintenance', 'Maintenance and Repair'),
    ('insurance', 'Insurance'),
    ('property expenses', 'Property Expenses'),
    ('professional fees', 'Labour Expenses'),
    ('financial', 'Financial Expenses'),
    ('general', 'General Expenses'),
    ('selling distribution', 'Administrative Expenses'),
    ('administrative', 'Administrative Expenses'),
)


class DebitType(models.Model):
    PURCHASE = 'purchase'
    DIRECT = 'direct'
    INDIRECT = 'indirect'
    MISCELLANEOUS = 'miscellaneous'

    TYPE_CHOICES = (
        (PURCHASE, 'Purchase'),
        (DIRECT, 'Direct'),
        (INDIRECT, 'Indirect'),
        (MISCELLANEOUS, 'Miscellaneous'),
    )

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    parent_type = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Debit(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField(default=0)
    reason = models.TextField(blank=True, null=True)
    debit_type = models.ForeignKey(DebitType, on_delete=models.CASCADE, null=True)

    def get_total_amount(self):
        subdebit_amounts = self.subdebit.aggregate(total_sum=Sum('amount'))['total_sum']
        return subdebit_amounts or self.amount

    def __str__(self):
        return self.name


Quantity_Choice = (
    ('kgs', 'KGS'),
    ('pieces', 'Pieces'),
)

Payment_Type = (
    ('cash', 'Cash'),
    ('upi', 'UPI'),
    ('cheque', 'Cheque'),
    ('net banking', 'Net Banking'),
)


class SubDebit(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    quantity_type = models.CharField(max_length=20, choices=Quantity_Choice, default='kgs')
    price = models.FloatField(default=0.0, null=True, blank=True)
    cgst = models.FloatField(default=0.0, null=True, blank=True)
    sgst = models.FloatField(default=0.0, null=True, blank=True)
    sub_amount = models.FloatField(default=0)
    amount = models.FloatField()
    date = models.DateField()
    reason = models.TextField(null=True, blank=True)
    debit = models.ForeignKey(Debit, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=100, choices=Payment_Type, default='cash')

    def __str__(self):
        return self.name

    @property
    def cgst_amount(self):
        amt = 0
        if self.cgst:
            amt = (self.price * self.quantity) * self.cgst / 100
        else:
            None

        return amt

    @property
    def sgst_amount(self):
        amt = 0
        if self.sgst:
            amt = (self.price * self.quantity) * self.sgst / 100
        else:
            None
        return amt

    @property
    def amount_without_gst(self):
        return self.amount - (self.sgst_amount + self.cgst_amount)


class Balance(models.Model):
    CHOICES = [
        ('Liability', 'Liability'),
        ('Asset', 'Asset'),
    ]

    name = models.CharField(max_length=100)
    reason = models.TextField(blank=True, null=True)
    balance_type = models.CharField(max_length=10, choices=CHOICES)

    def __str__(self):
        return self.name


class BalanceObject(models.Model):
    balance = models.ForeignKey(Balance, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sub_amount = models.FloatField(default=0)
    amount = models.FloatField()
    cgst = models.FloatField(default=0.0, null=True, blank=True)
    sgst = models.FloatField(default=0.0, null=True, blank=True)
    date = models.DateField()
    payment_mode = models.CharField(max_length=20, choices=Payment_Type)

    def __str__(self):
        return f"{self.name} - {self.amount}"


