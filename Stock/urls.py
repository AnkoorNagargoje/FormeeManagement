from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view),
    path('stock/', views.stock_view),
    path('stock/add_product/', views.add_product_view),
    path('stock/product/<str:code>/', views.edit_product_view),
    path('stock/stock_report/', views.stock_report),
    path('stock/generate_quantity_summary_csv/', views.generate_quantity_summary_csv, name='generate_quantity_summary_csv'),
]