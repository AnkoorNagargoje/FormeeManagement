from Stock.models import Product
from django.db import models


SALE_CHOICE = (
    ('super market', 'Super Market'),
    ('franchise', 'Franchise'),
    ('normal', 'Normal Customer'),
    ('exhibition', 'Exhibition'),
)


class Customer(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    district = models.CharField(max_length=100, default='')
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

    def save(self, *args, **kwargs):
        self.order_total = max(0, self.order_total)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} - {self.id}"

    def cgst(self):
        return self.order_total * 6 / 100

    def sgst(self):
        return self.order_total * 6 / 100

    def total_gst(self):
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


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def franchise_item_total(self):
        return self.product.franchise_price * self.quantity

    def store_item_total(self):
        return self.product.store_price * self.quantity

    def customer_item_total(self):
        return self.product.price * self.quantity


class SalesReturn(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"Return for Order {self.order.id} by {self.customer.name}"


class ReturnItem(models.Model):
    sales_return = models.ForeignKey(SalesReturn, on_delete=models.CASCADE)
    product = models.ForeignKey(OrderItem, on_delete=models.CASCADE, default=None)
    quantity = models.PositiveIntegerField(default=1)
    return_total = models.FloatField(default=0)
    payment_status = models.CharField(max_length=30, default='')
    payment_type = models.CharField(max_length=20, default='')

    def __str__(self):
        return f"ReturnItem of {self.sales_return.id} - {self.id}"




