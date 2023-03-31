from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, Order, Product, OrderItem
from .forms import OrderForm, OrderItemForm, CustomerForm
from django.contrib.auth.decorators import login_required
from Stock.models import Quantity
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO


@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'billing.html', {'customers': customers})


@login_required
def add_new_customer(request):
    form = CustomerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(customer_list)
    return render(request, 'add_new_customer.html', {'form': form})


@login_required
def order_list(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    orders = customer.order_set.all()
    form = OrderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        order = form.save(commit=False)
        order.customer = customer
        order_update = Customer.objects.get(id=customer_id)
        order_update.no_of_order = order_update.no_of_order + 1
        order_update.save()
        order.save()
        return redirect('order_detail', customer_id=customer.id, order_id=order.id)
    return render(request, 'order_list.html', {'customer': customer, 'orders': orders, 'form': form})


@login_required
def order_detail(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    order_items = order.orderitem_set.all()

    form = OrderItemForm(request.POST or None)
    if form.is_valid():
        order_item = form.save(commit=False)
        order_item.order = order
        order_item.save()
        product = order_item.product
        product.stock -= order_item.quantity
        product.save()
        quantity_object = Quantity.objects.create(product_code=order_item.product,
                                                  out_quantity=order_item.quantity)
        quantity_object.save()
        order.order_total += order_item.quantity * product.price
        order.save()
        return redirect('order_detail', customer_id=customer.id, order_id=order.id)

    return render(request, 'order_detail.html', {'form': form, 'customer': customer, 'order': order, 'order_items': order_items})


from django.template.loader import get_template


def generate_invoice(request, order_id):
    # Fetch the order and related data
    order = Order.objects.get(id=order_id)
    customer = order.customer
    order_items = OrderItem.objects.filter(order=order)
    total_amount = order.order_total

    # Render the HTML template
    template = get_template('invoice.html')
    context = {'order': order, 'customer': customer, 'order_items': order_items, 'total_amount': total_amount}
    html = template.render(context)

    # Create a PDF file using xhtml2pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{order_id}.pdf'
    pisa.CreatePDF(html, dest=response, encoding='utf-8')

    return response

from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.conf import settings
import os

def generate_invoice_pdf(request, order_id):
    # Get the template
    template = get_template('invoice.html')
    order = Order.objects.get(id=order_id)
    customer = order.customer
    order_items = OrderItem.objects.filter(order=order)
    total_amount = order.order_total

    # Define the context for the template
    context = {
        'order': order,
        'STATIC_ROOT': settings.STATIC_ROOT
    }

    # Render the template with the context
    html = template.render(context)

    # Define the filename for the PDF file
    filename = f"{order.customer.name}_Invoice.pdf"

    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Create the PDF file
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=fetch_resources)

    # Return the PDF file
    if pisa_status.err:
        return HttpResponse('There was an error creating the PDF file')
    else:
        return response

def fetch_resources(uri, rel):
    """
    Callback function used by xhtml2pdf to fetch external resources (e.g. images)
    """
    path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    return path


def invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    customer = order.customer
    order_items = OrderItem.objects.filter(order=order)
    total_amount = order.order_total

    # Render the HTML template
    return render(request, 'invoice.html', {'order': order, 'customer': customer, 'order_items': order_items, 'total_amount': total_amount})





