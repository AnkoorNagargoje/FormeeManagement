from Stock.models import Product
from django.db import models
from django.db.models import Sum


SALE_CHOICE = (
    ('super market', 'Distributor'),
    ('franchise', 'Franchise'),
    ('normal', 'Normal Customer'),
    ('exhibition', 'Exhibition'),
)


class Customer(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    district = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=20, default='Maharashtra')
    email = models.EmailField()
    gstin = models.CharField(max_length=100)
    fssai = models.CharField(max_length=100)
    phone = models.PositiveBigIntegerField()
    birth_date = models.CharField(max_length=10, default="")
    order_type = models.CharField(max_length=30, choices=SALE_CHOICE, default='normal')
    franchise_id = models.CharField(default="", max_length=5)

    def __str__(self):
        return self.name

    @property
    def no_of_order(self):
        return self.order_set.count()


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=False, editable=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    order_total = models.FloatField(default=0)
    payment_status = models.CharField(max_length=30, default='Pending')
    payment_type = models.CharField(max_length=20, default='')
    discount = models.PositiveIntegerField(default=0, null=True, blank=True)
    delivery = models.FloatField(default=0, null=True, blank=True)
    invoice_number = models.PositiveIntegerField(default=0, blank=True, null=True)
    payment_terms = models.CharField(max_length=100, default='', blank=True, null=True)
    ref_number = models.CharField(default='', max_length=24, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.order_total = max(0, self.order_total)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} - {self.id}"

    def cgst(self):
        return self.order_total * 6 / 100

    def sgst(self):
        return self.order_total * 6 / 100

    def igst(self):
        if self.customer.state != 'Maharashtra':
            return self.order_total * 12 / 100
        else:
            return 0

    def total_gst(self):
        if self.customer.state != 'Maharashtra':
            return self.igst()
        else:
            return self.sgst() + self.cgst()

    def order_total_with_gst(self):
        return round(self.order_total + self.total_gst(), 0)

    def normal_order_total(self):
        total = self.order_total
        rounded_total = total.__round__(0)
        return rounded_total

    def order_total_with_delivery(self):
        total = round(self.order_total + self.delivery, 0)
        return total

    def order_total_with_gst_and_delivery(self):
        return round(self.order_total_with_gst() + self.delivery, 0)

    def real_order_total(self):
        real = round((self.order_total * 100) / (100 - self.discount), 0)
        return real

    def discount_amount(self):
        return self.real_order_total() - self.order_total

    def get_total_amount_based_on_type(self):
        if self.customer.order_type == 'normal':
            return self.order_total
        else:
            return self.order_total_with_gst()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(default=0)
    batchno = models.CharField(max_length=20, default='')

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def item_total(self):
        return self.price * self.quantity


class SalesReturn(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    sales_return_total = models.FloatField(default=0.0)

    def update_sales_return_total(self):
        total_return = self.returnitem_set.aggregate(total=Sum('return_total'))['total']
        self.sales_return_total = round(total_return, 2)
        self.save()

    def __str__(self):
        return f"Return for Order {self.order.id} by {self.customer.name}"


class ReturnItem(models.Model):
    sales_return = models.ForeignKey(SalesReturn, on_delete=models.CASCADE)
    product = models.ForeignKey(OrderItem, on_delete=models.CASCADE, default=None)
    quantity = models.PositiveIntegerField(default=1)
    return_total = models.FloatField(default=0)
    payment_status = models.CharField(max_length=30, default='')
    payment_type = models.CharField(max_length=20, default='')
    price = models.FloatField(default=0)

    def __str__(self):
        return f"ReturnItem of {self.sales_return.id} - {self.id}"




