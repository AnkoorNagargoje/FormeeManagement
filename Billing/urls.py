from django.urls import path
from . import views


urlpatterns = [
    path('billing/', views.customer_list, name='customer_list'),
    path('billing/add_customer/', views.add_new_customer, name='add_new_customer'),
    path('billing/<int:customer_id>/orders/', views.order_list, name='order_list'),
    path('billing/<int:customer_id>/orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('billing/<int:customer_id>/orders/<int:order_id>/<int:order_item_id>/edit/', views.order_item_edit, name='order_item_edit'),
    path('billing/<int:customer_id>/orders/<int:order_id>/<int:order_item_id>/delete/', views.order_item_delete, name='order_item_delete'),
    path('billing/<int:order_id>/invoice/', views.generate_invoice),
    path('invoice/<int:order_id>/', views.invoice),
]