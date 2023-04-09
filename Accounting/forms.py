from django import forms
from .models import *


class CreditForm(forms.ModelForm):
    name = forms.CharField()
    amount = forms.FloatField()
    invoice_number = forms.IntegerField(required=False)
    transaction_number = forms.IntegerField(required=False)
    date = forms.DateField(required=False, widget=forms.widgets.DateInput(format=['%d-%m-%Y'], attrs={'type': 'date'}))

    class Meta:
        model = Credit
        fields = ['name', 'amount', 'invoice_number', 'transaction_number', 'date']


class DebitForm(forms.ModelForm):
    name = forms.CharField()
    amount = forms.FloatField()
    reason = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Debit
        fields = ['name', 'amount', 'reason']
