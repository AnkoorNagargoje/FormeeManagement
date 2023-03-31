from django.urls import path
from .views import home_view, add_product_view, stock_view, edit_product_view

urlpatterns = [
    path('', home_view),
    path('stock/', stock_view),
    path('stock/add_product/', add_product_view),
    path('stock/<str:code>/', edit_product_view),
]