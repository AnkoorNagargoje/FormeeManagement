from django import forms
from .models import Customer, Order, OrderItem
from Stock.models import Product

SALE_CHOICE = (
    ('super market', 'Super Market'),
    ('franchise', 'Franchise'),
    ('studio', 'Studio'),
    ('normal', 'Normal Customer'),
)


class CustomerForm(forms.ModelForm):
    name = forms.CharField()
    address = forms.CharField(widget=forms.Textarea)
    district = forms.CharField()
    email = forms.EmailField()
    gstin = forms.CharField(required=False)
    fssai = forms.CharField(required=False)
    phone = forms.IntegerField()
    no_of_order = forms.IntegerField(required=False)
    order_type = forms.ChoiceField(choices=SALE_CHOICE)

    class Meta:
        model = Customer
        fields = ['name', 'address', 'district', 'email', 'gstin', 'fssai', 'phone', 'no_of_order', 'order_type']


class OrderForm(forms.ModelForm):
    payment_status = forms.CharField(required=False)

    class Meta:
        model = Order
        fields = ('payment_status',)


class OrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label='Product', to_field_name='id')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].label_from_instance = lambda obj: obj.name

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity',)
