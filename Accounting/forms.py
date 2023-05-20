from django import forms
from .models import *


class CreditForm(forms.ModelForm):
    name = forms.CharField()
    amount = forms.FloatField()
    invoice_number = forms.IntegerField(required=False)
    transaction_number = forms.IntegerField(required=False)
    payment_type = forms.CharField(required=False)
    date = forms.DateField(required=False, widget=forms.widgets.DateInput(format=['%d-%m-%Y'], attrs={'type': 'date'}))
    account_no = forms.CharField(required=False)
    bank_name = forms.CharField(required=False)

    class Meta:
        model = Credit
        fields = ['name', 'amount', 'invoice_number', 'payment_type', 'transaction_number', 'date', 'account_no', 'bank_name']


class DebitForm(forms.ModelForm):
    name = forms.CharField()
    amount = forms.FloatField()
    reason = forms.CharField(widget=forms.Textarea, required=False)
    person = forms.CharField()
    how = forms.ChoiceField(choices=HOW_CHOICES)

    class Meta:
        model = Debit
        fields = ['name', 'amount', 'reason', 'person', 'how']
