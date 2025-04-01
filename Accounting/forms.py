from django import forms
from .models import *


class CreditForm(forms.ModelForm):
    name = forms.CharField()
    amount = forms.FloatField()
    transaction_number = forms.CharField(required=False)
    payment_type = forms.CharField(required=False)
    date = forms.DateField(label='Created at', widget=forms.DateInput(attrs={'type': 'date'}),
                                 input_formats=['%Y-%m-%d'])
    cheque_no = forms.CharField(required=False)
    bank_name = forms.CharField(required=False)
    note = forms.CharField(required=False)
    credit_type = forms.CharField(required=False)

    class Meta:
        model = Credit
        fields = ['name', 'amount', 'payment_type', 'transaction_number', 'date', 'cheque_no',
                  'bank_name', 'note', 'credit_type']


class DebitTypeForm(forms.ModelForm):
    class Meta:
        model = DebitType
        fields = ['name']


class DebitTypeEditForm(forms.ModelForm):
    class Meta:
        model = DebitType
        fields = '__all__'


class DebitForm(forms.ModelForm):
    name = forms.CharField()
    reason = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Debit
        fields = ['name', 'reason']


class EditDebitForm(forms.ModelForm):
    amount = forms.FloatField(required=False)
    reason = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Debit
        fields = '__all__'


class SubDebitForm(forms.ModelForm):
    name = forms.CharField()
    quantity = forms.IntegerField(required=False)
    price = forms.FloatField(required=False)
    quantity_type = forms.ChoiceField(choices=Quantity_Choice, required=False)
    cgst = forms.IntegerField(required=False)
    sgst = forms.IntegerField(required=False)
    amount = forms.FloatField()
    reason = forms.CharField(widget=forms.Textarea, required=False)
    date = forms.DateField(label='Date', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%Y-%m-%d'])
    payment_type = forms.ChoiceField(choices=Payment_Type)

    class Meta:
        model = SubDebit
        fields = ['name', 'quantity', 'price', 'quantity_type', 'cgst', 'sgst', 'amount', 'reason', 'date', 'payment_type']


class BalanceForm(forms.ModelForm):
    class Meta:
        model = Balance
        fields = '__all__'