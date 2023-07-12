from django.urls import path
from . import views


urlpatterns = [
    path('billing/', views.customer_list, name='customer_list'),
    path('<int:customer_id>/edit/', views.edit_customer, name='edit-customer.html'),
    path('billing/add_customer/', views.add_new_customer, name='add_new_customer'),
    path('billing/get-gst-report/', views.get_gst_report, name='get-gst-report'),
    path('billing/get-sales-report/', views.get_sales_report, name='get_sales_report'),
    path('billing/get-gst-report/export_csv/', views.export_report_to_csv, name='export_report_to_csv'),
    path('billing/add_customer/<int:customer_id>/extended/', views.customer_extended_form, name='customer_extended_form'),

    path('billing/<int:customer_id>/orders/', views.order_list, name='order_list'),
    path('ledger_view/<int:customer_id>/', views.ledger_view, name='ledger_view'),
    path('generate_ledger/<int:customer_id>/<str:start_date>/<str:end_date>/', views.generate_ledger, name='generate_ledger'),
    path('billing/<int:customer_id>/orders/<int:order_id>/delete/', views.order_delete, name='order_delete'),
    path('billing/<int:customer_id>/orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('billing/<int:customer_id>/orders/<int:order_id>/register_sales_return/', views.register_sales_return, name='register_sales_return'),
    path('billing/<int:customer_id>/orders/<int:order_id>/sales_return/<int:sales_return_id>/', views.returned_items,
         name='returned_items'),
    path('billing/<int:customer_id>/order/<int:order_id>/cash/', views.order_paid_cash, name='order_paid_cash'),
    path('billing/<int:customer_id>/order/<int:order_id>/upi/', views.order_paid_upi, name='order_paid_upi'),
    path('billing/<int:customer_id>/order/<int:order_id>/net-banking/', views.order_paid_net, name='order_paid_net'),
    path('billing/<int:customer_id>/order/<int:order_id>/cheque/', views.order_paid_cheque, name='order_paid_cheque'),
    path('billing/<int:customer_id>/order/<int:order_id>/5-dis/', views.order_dis_five, name='order_dis_five'),
    path('billing/<int:customer_id>/order/<int:order_id>/10-dis/', views.order_dis_ten, name='order_dis_ten'),
    path('billing/<int:customer_id>/order/<int:order_id>/20-dis/', views.order_dis_twenty, name='order_dis_twenty'),
    path('billing/<int:customer_id>/order/<int:order_id>/25-dis/', views.order_dis_twenty_five, name='order_dis_twenty_five'),
    path('billing/<int:customer_id>/orders/<int:order_id>/<int:order_item_id>/edit/', views.order_item_edit, name='order_item_edit'),
    path('billing/<int:customer_id>/orders/<int:order_id>/<int:order_item_id>/delete/', views.order_item_delete, name='order_item_delete'),
    path('billing/<int:order_id>/invoice/', views.generate_invoice),
    path('invoice/<int:order_id>/', views.invoice),
]