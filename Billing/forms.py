from django import forms
from .models import *
from Stock.models import Product

SALE_CHOICE = (
    ('normal', 'Normal Customer'),
    ('super market', 'Super Market'),
    ('franchise', 'Franchise'),
)


class CustomerForm(forms.ModelForm):
    name = forms.CharField()
    address = forms.CharField(widget=forms.Textarea, required=False)
    district = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    gstin = forms.CharField(required=False)
    fssai = forms.CharField(required=False)
    phone = forms.IntegerField()
    birth_date = forms.DateField(input_formats=['%d/%m'], required=False)
    no_of_order = forms.IntegerField(required=False)
    order_type = forms.ChoiceField(choices=SALE_CHOICE, required=False)

    class Meta:
        model = Customer
        fields = ['name', 'address', 'district', 'email', 'gstin', 'fssai', 'phone', 'birth_date', 'no_of_order', 'order_type']


class OrderForm(forms.ModelForm):
    payment_status = forms.CharField(required=False)

    class Meta:
        model = Order
        fields = ('payment_status',)


class OrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all().order_by('code'), label='Product', to_field_name='id')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].label_from_instance = lambda obj: obj.name

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity',)
