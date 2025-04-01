from django.contrib import admin
from .models import *


class CreditAdmin(admin.ModelAdmin):
    list_display = ['name', 'receipt_number', 'amount']


class DebitTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']


class DebitAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'reason']


class SubDebitAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'reason']


class BalanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'balance_type', 'reason']


class BalanceObjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'date']


admin.site.register(Credit, CreditAdmin)
admin.site.register(DebitType, DebitTypeAdmin)
admin.site.register(Debit, DebitAdmin)
admin.site.register(SubDebit, SubDebitAdmin)
admin.site.register(Balance, BalanceAdmin)
admin.site.register(BalanceObject, BalanceObjectAdmin)