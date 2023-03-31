from django.contrib import admin
from .models import *


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'price', 'stock']


class QuantityAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'in_quantity', 'out_quantity']


admin.site.register(Product, ProductAdmin)
admin.site.register(Quantity, QuantityAdmin)
