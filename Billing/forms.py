from django import forms
from .models import *
from Stock.models import Product

SALE_CHOICE = (
    ('normal', 'Normal Customer'),
    ('super market', 'Distributor'),
    ('franchise', 'Franchise'),
    ('exhibition', 'Exhibition'),
)


class CustomerForm(forms.ModelForm):
    name = forms.CharField()
    phone = forms.IntegerField(required=False)
    birth_date = forms.CharField(required=False)
    no_of_order = forms.IntegerField(required=False)
    order_type = forms.ChoiceField(choices=SALE_CHOICE, required=False)

    class Meta:
        model = Customer
        fields = ['name', 'phone', 'birth_date', 'no_of_order', 'order_type']


class CustomerProfileForm(forms.ModelForm):
    address = forms.CharField(widget=forms.Textarea)
    district = forms.CharField(required=False)
    state = forms.CharField(required=False)
    email = forms.CharField(required=False)
    gstin = forms.CharField(required=False)
    fssai = forms.CharField(required=False)
    franchise_id = forms.CharField(required=False)

    class Meta:
        model = Customer
        fields = ['address', 'district', 'state', 'email', 'gstin', 'fssai', 'franchise_id']


class OrderForm(forms.ModelForm):
    created_at = forms.DateField(label='Created at', widget=forms.DateInput(attrs={'type': 'date'}),
                                 input_formats=['%Y-%m-%d'])
    payment_status = forms.CharField(required=False)
    invoice_number = forms.IntegerField(required=False)
    ref_number = forms.CharField(required=False)

    class Meta:
        model = Order
        fields = ('created_at', 'payment_status', 'invoice_number', 'ref_number')

    def clean_created_at(self):
        created_at = self.cleaned_data['created_at']
        return created_at


class DeliveryForm(forms.ModelForm):
    delivery = forms.FloatField(required=False)
    discount = forms.IntegerField(required=False)
    payment_terms = forms.CharField(required=False)

    class Meta:
        model = Order
        fields = ['delivery', 'discount', 'payment_terms']

    def __init__(self, *args, **kwargs):
        order = kwargs.pop('order', None)
        super().__init__(*args, **kwargs)
        if order:
            self.fields['payment_terms'].widget.attrs.update({'placeholder': order.payment_terms})


class OrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all().order_by('code'), label='Product', to_field_name='id')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].label_from_instance = lambda obj: f"{obj.barcode} - {obj.size} - {obj.name}"

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity', 'price', 'batchno',)


class ReturnedItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=None)
    quantity = forms.IntegerField(initial=1)

    class Meta:
        model = ReturnItem
        fields = ['product', 'quantity']

    def __init__(self, order_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        order_items = OrderItem.objects.filter(order_id=order_id)
        self.fields['product'].queryset = order_items
        self.fields['product'].label_from_instance = lambda obj: f"{obj.product.barcode} - {obj.product.size} - {obj.product.name}"
        def clean(self):
            cleaned_data = super().clean()
            product = cleaned_data.get('product')
            quantity = cleaned_data.get('quantity')
            return cleaned_data


class SalesReturnForm(forms.ModelForm):
    class Meta:
        model = SalesReturn
        fields = '__all__'

    def __init__(self, order_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        order_items = OrderItem.objects.filter(order_id=order_id)
        self.fields['returned_items'].queryset = order_items
