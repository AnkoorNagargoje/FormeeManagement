from django.urls import path
from . import views


urlpatterns = [
    path('accounting/', views.accounting),
    path('accounting/add_credit/', views.add_credit),
    path('accounting/add_debit/', views.add_debit),
]