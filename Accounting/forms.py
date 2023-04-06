from django import forms
from .models import *


class CreditForm(forms.ModelForm):
    name = forms.CharField()
    amount = forms.FloatField()
    invoice_number = forms.IntegerField(required=False)

    class Meta:
        model = Credit
        fields = ['name', 'amount', 'invoice_number']


class DebitForm(forms.ModelForm):
    name = forms.CharField()
    amount = forms.FloatField()
    reason = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Debit
        fields = ['name', 'amount', 'reason']
