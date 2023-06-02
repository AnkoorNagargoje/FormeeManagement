from django.urls import path
from . import views


urlpatterns = [
    path('accounting/', views.accounting),
    path('accounting/pnl/', views.pnl),
    path('accounting/pnl/sales/', views.sales),
    path('accounting/pnl/debits/', views.total_expenses),
    path('accounting/cr/', views.credits_view),
    path('accounting/cr/add_credit/', views.add_credit),
    path('accounting/cr/credit/<int:credit_id>/edit/', views.edit_credit),
    path('accounting/de/', views.debits_view),
    path('accounting/de/add_debit/', views.add_debit),
    path('accounting/de/debit/<int:debit_id>/edit/', views.edit_debit),
]