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
    birth_date = models.DateField(blank=True, null=True,)
    order_type = models.CharField(max_length=30, choices=SALE_CHOICE, default='normal')
    no_of_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    order_total = models.FloatField(default=0)
    payment_status = models.CharField(max_length=30, default='Pending')
    payment_type = models.CharField(max_length=20, default='')
    discount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.customer} - {self.id}"

    def franchise_order_total(self):
        without_gst = self.order_total * 100 / 112
        return without_gst - without_gst * 25 / 100

    def store_order_total(self):
        without_gst = self.order_total * 100 / 112
        return without_gst - without_gst * 20 / 100

    def franchise_cgst(self):
        return self.franchise_order_total() * 6 / 100

    def store_cgst(self):
        return self.store_order_total() * 6 / 100

    def franchise_sgst(self):
        return self.franchise_order_total() * 6 / 100

    def store_sgst(self):
        return self.store_order_total() * 6 / 100

    def franchise_gst(self):
        return self.franchise_cgst() + self.franchise_sgst()

    def store_gst(self):
        return self.store_cgst() + self.store_sgst()

    def franchise_cgst_total(self):
        total = self.franchise_order_total() + self.franchise_cgst() + self.franchise_sgst()
        rounded_total = total.__round__(2)
        return rounded_total

    def store_cgst_total(self):
        total = self.store_order_total() + self.store_cgst() + self.store_sgst()
        rounded_total = total.__round__(2)
        return rounded_total

    def normal_order_total(self):
        total = self.order_total
        rounded_total = total.__round__(2)
        return rounded_total

    def real_order_total(self):
        real = round((self.order_total * 100) / (100 - self.discount))
        return real



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
