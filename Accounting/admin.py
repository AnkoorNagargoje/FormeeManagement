from django.contrib import admin
from .models import *


class CreditAdmin(admin.ModelAdmin):
    list_display = ['name', 'invoice_number', 'amount']


class DebitTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']


class DebitAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'reason']


class SubDebitAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'reason']


admin.site.register(Credit, CreditAdmin)
admin.site.register(DebitType, DebitTypeAdmin)
admin.site.register(Debit, DebitAdmin)
admin.site.register(SubDebit, SubDebitAdmin)