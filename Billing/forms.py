from django import forms
from .models import *
from Stock.models import Product

SALE_CHOICE = (
    ('normal', 'Normal Customer'),
    ('super market', 'Super Market'),
    ('franchise', 'Franchise'),
    ('exhibition', 'Exhibition'),
)


class CustomerForm(forms.ModelForm):
    name = forms.CharField()
    phone = forms.IntegerField()
    birth_date = forms.DateField(input_formats=['%d/%m'], required=False)
    no_of_order = forms.IntegerField(required=False)
    order_type = forms.ChoiceField(choices=SALE_CHOICE, required=False)

    class Meta:
        model = Customer
        fields = ['name', 'phone', 'birth_date', 'no_of_order', 'order_type']


class CustomerProfileForm(forms.ModelForm):
    address = forms.CharField(widget=forms.Textarea)
    district = forms.CharField()
    email = forms.EmailField()
    gstin = forms.CharField()
    fssai = forms.CharField()
    franchise_id = forms.CharField()

    class Meta:
        model = Customer
        fields = ['address', 'district', 'email', 'gstin', 'fssai', 'franchise_id']


class OrderForm(forms.ModelForm):
    created_at = forms.DateField(label='Created at', widget=forms.DateInput(attrs={'type': 'date'}),
                                 input_formats=['%Y-%m-%d'])
    payment_status = forms.CharField(required=False)

    class Meta:
        model = Order
        fields = ('created_at' ,'payment_status',)

    def clean_created_at(self):
        created_at = self.cleaned_data['created_at']
        # Add any additional validation or processing for the created_at field here
        return created_at


class OrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all().order_by('code'), label='Product', to_field_name='id')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].label_from_instance = lambda obj: obj.name

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity',)
