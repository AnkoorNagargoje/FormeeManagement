from django import forms
from .models import Product, Quantity


class ProductForm(forms.ModelForm):
    name = forms.CharField(max_length=300)
    code = forms.CharField(max_length=4)
    size = forms.CharField(max_length=20)
    price = forms.FloatField()
    stock = forms.IntegerField()

    class Meta:
        model = Product
        fields = ['name', 'code','size', 'price', 'stock']


class QuantityForm(forms.ModelForm):
    in_quantity = forms.IntegerField(required=False)
    out_quantity = forms.IntegerField(required=False)

    class Meta:
        model = Quantity
        fields = ['in_quantity', 'out_quantity']