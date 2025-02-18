from django.urls import path
from . import views

urlpatterns = [
    path('accounting/', views.accounting),

    path('accounting/balance/', views.balance_sheet),
    path('accounting/balance/add/', views.add_balance),

    path('accounting/pnl/', views.pnl),
    path('accounting/pnl/sales/', views.sales),
    path('accounting/pnl/debits/', views.total_expenses),

    path('accounting/cr/', views.credits_view),
    path('accounting/cr/<str:credit_type>/', views.credits_type_view),
    path('accounting/cr/<str:credit_type>/add_credit/', views.add_credit),
    path('accounting/cr/<str:credit_type>/<int:credit_id>/edit/', views.edit_credit),

    path('accounting/de/', views.debits_view),
    path('accounting/de/<str:debit_type_param>/', views.debit_type_view),
    path('accounting/de/<str:debit_type>/add_debit_type/', views.add_debit_type_form),
    path('accounting/de/<str:debit_type>/<int:debit_type_id>/debit/', views.debits_by_type_view),
    path('accounting/de/<str:debit_type>/<int:debit_type_id>/debit/add_debit/', views.add_debits_form),
    path('accounting/de/<str:debit_type>/<int:debit_type_id>/edit/', views.edit_debit_type_form),
    path('accounting/de/<str:debit_type>/<int:debit_type_id>/debit/<int:debit_id>/', views.sub_debits_view),
    path('accounting/de/<str:debit_type>/<int:debit_type_id>/debit/<int:debit_id>/edit/', views.edit_debit_form),
    path('accounting/de/<str:debit_type>/<int:debit_type_id>/debit/<int:debit_id>/add_debit/', views.add_subdebits_form),
    path('accounting/de/<str:debit_type>/<int:debit_type_id>/debit/<int:debit_id>/<int:sub_debit_id>/', views.sub_debits_expand_view),
    path('accounting/de/<str:debit_type>/<int:debit_type_id>/debit/<int:debit_id>/<int:sub_debit_id>/edit/', views.sub_debits_edit_view),

    path('accounting/de/add_debit/', views.add_debit),
    path('accounting/de/debit/<int:debit_id>/edit/', views.edit_debit),

    path('accounting/debits_csv/', views.all_debits_csv, name='all_debits_csv'),
    path('accounting/credits_csv/', views.all_credits_csv, name='all_credits_csv'),
]
