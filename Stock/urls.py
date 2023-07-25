from django.urls import path
from .views import *

urlpatterns = [
    path('', home_view),
    path('stock/', stock_view),
    path('stock/add_product/', add_product_view),
    path('stock/<str:code>/', edit_product_view),
    path('stock/stock_report/', stock_report),
]