from django.contrib import admin
from .models import Credit, Debit


class CreditAdmin(admin.ModelAdmin):
    list_display = ['name', 'invoice_number', 'amount']


class DebitAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'reason']


admin.site.register(Credit, CreditAdmin)
admin.site.register(Debit, DebitAdmin)