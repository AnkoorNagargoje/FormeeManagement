from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=4, unique=True)
    size = models.CharField(max_length=20, default='200gm')
    price = models.FloatField()
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class Quantity(models.Model):
    product_code = models.ForeignKey(Product, on_delete=models.CASCADE)
    in_quantity = models.IntegerField(blank=True, null=True)
    out_quantity = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_code