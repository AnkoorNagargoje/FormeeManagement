from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=4, unique=True)
    barcode = models.BigIntegerField(default=0)
    size = models.CharField(max_length=20, default='200gm')
    hsn_code = models.CharField(max_length=10, default=210690)
    price = models.FloatField()
    franchise_price = models.FloatField(default=0)
    store_price = models.FloatField(default=0)
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class Quantity(models.Model):
    product_code = models.ForeignKey(Product, on_delete=models.CASCADE)
    in_quantity = models.IntegerField(blank=True, null=True)
    out_quantity = models.IntegerField(blank=True, null=True)
    invoice_number = models.PositiveIntegerField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    note = models.CharField(default='', max_length=100)

    def __str__(self):
        return str(self.product_code.code)