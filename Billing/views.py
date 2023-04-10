from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, Order, Product, OrderItem
from .forms import OrderForm, OrderItemForm, CustomerForm
from django.contrib.auth.decorators import login_required
from Stock.models import Quantity
from django.http import HttpResponse
from xhtml2pdf import pisa
from num2words import num2words
from django.template.loader import get_template
from django.contrib import messages


@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('pk')

    customer_search = request.GET.get('customer_search')
    if customer_search != '' and customer_search is not None:
        customers = Customer.objects.filter(name__icontains=customer_search)

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
    orders = customer.order_set.all().order_by('-created_at')

    order_invoice_search = request.GET.get('order_invoice_search')
    if order_invoice_search != '' and order_invoice_search is not None:
        orders = Order.objects.filter(customer=customer, pk__contains=order_invoice_search)

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


def order_item_edit(request, customer_id, order_id, order_item_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    order_item = get_object_or_404(OrderItem, id=order_item_id, order=order)
    old_quantity = order_item.quantity
    form = OrderItemForm(request.POST or None, instance=order_item)
    if form.is_valid():
        new_order_item = form.save(commit=False)
        product = order_item.product
        if new_order_item.quantity > old_quantity:
            diff = new_order_item.quantity - old_quantity
            product.stock -= diff
            order.order_total += order_item.product.price * diff
        else:
            diff = old_quantity - new_order_item.quantity
            product.stock += diff
            order.order_total -= order_item.product.price * diff
        product.save()
        new_order_item.save()
        order.save()
        messages.success(request, product.stock)
        return redirect('order_detail', customer_id=customer.id, order_id=order.id)
    return render(request, 'order_item_edit.html', {'form': form, 'customer': customer, 'order': order, 'order_item': order_item})


def order_item_delete(request, customer_id, order_id, order_item_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    order_item = get_object_or_404(OrderItem, id=order_item_id, order=order)
    product = order_item.product

    # Add the quantity back to the product stock
    product.stock += order_item.quantity
    product.save()

    # Subtract the order item total from the order total
    order.order_total -= order_item.product.price * order_item.quantity
    order.save()

    # Delete the order item
    order_item.delete()

    return redirect('order_detail', customer_id=customer.id, order_id=order.id)


def generate_invoice(request, order_id):
    # Fetch the order and related data
    order = Order.objects.get(id=order_id)
    customer = order.customer
    order_items = OrderItem.objects.filter(order=order)
    total_amount = order.order_total
    total_amount_in_words_franchise = num2words(order.franchise_cgst_total())
    total_amount_in_words_normal = num2words(order.normal_order_total())
    total_amount_in_words_store = num2words(order.store_cgst_total())
    total_amount_in_words_exhibition = num2words(order.normal_order_total())

    # Render the HTML template
    template = get_template('invoice.html')
    context = {'order': order, 'customer': customer, 'order_items': order_items, 'total_amount': total_amount,
               'total_amount_in_words_franchise': total_amount_in_words_franchise,
               'total_amount_in_words_normal': total_amount_in_words_normal,
               'total_amount_in_words_store': total_amount_in_words_store,
               'total_amount_in_words_exhibition': total_amount_in_words_exhibition,
               }
    html = template.render(context)

    # Create a PDF file using xhtml2pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Invoice-{customer.name}-{order_id}.pdf'
    pisa.CreatePDF(html, dest=response, encoding='utf-8')

    return response


def invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    customer = order.customer
    order_items = OrderItem.objects.filter(order=order)
    total_amount = order.order_total

    # Render the HTML template
    return render(request, 'invoice_view.html', {'order': order, 'customer': customer, 'order_items': order_items, 'total_amount': total_amount})