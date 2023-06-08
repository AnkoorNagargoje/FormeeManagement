from django import forms
from .models import *


class CreditForm(forms.ModelForm):
    name = forms.CharField()
    amount = forms.FloatField()
    invoice_number = forms.IntegerField(required=False)
    transaction_number = forms.IntegerField(required=False)
    payment_type = forms.CharField(required=False)
    date = forms.DateField(label='Created at', widget=forms.DateInput(attrs={'type': 'date'}),
                                 input_formats=['%Y-%m-%d'])
    cheque_no = forms.CharField(required=False)
    bank_name = forms.CharField(required=False)
    note = forms.CharField(required=False)
    credit_type = forms.ChoiceField(choices=CREDIT_TYPE)

    class Meta:
        model = Credit
        fields = ['name', 'amount', 'invoice_number', 'payment_type', 'transaction_number', 'date', 'cheque_no',
                  'bank_name', 'note', 'credit_type']


class DirectDebitTypeForm(forms.ModelForm):
    class Meta:
        model = DebitType
        fields = ['name']


class DebitForm(forms.ModelForm):
    name = forms.CharField()
    reason = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Debit
        fields = ['name', 'reason']


class SubDebitForm(forms.ModelForm):
    name = forms.CharField()
    quantity = forms.IntegerField(required=False)
    price = forms.FloatField(required=False)
    quantity_type = forms.ChoiceField(choices=Quantity_Choice, required=False)
    amount = forms.FloatField()
    reason = forms.CharField(widget=forms.Textarea, required=False)
    date = forms.DateField(label='Date', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%Y-%m-%d'])

    class Meta:
        model = SubDebit
        fields = ['name', 'quantity', 'price', 'quantity_type', 'amount', 'reason', 'date']
