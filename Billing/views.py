from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, Order, Product, OrderItem
from .forms import OrderForm, OrderItemForm, CustomerForm, CustomerProfileForm
from django.contrib.auth.decorators import login_required
from Stock.models import Quantity
from xhtml2pdf import pisa
from num2words import num2words
from django.template.loader import get_template
from django.contrib import messages
from Accounting.models import Credit
from Accounting.views import edit_credit
import csv
from django.http import HttpResponse
from datetime import datetime
from django.core.paginator import Paginator


@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-pk')

    customer_search = request.GET.get('customer_search')
    if customer_search != '' and customer_search is not None:
        customers = Customer.objects.filter(name__icontains=customer_search)

    paginator = Paginator(customers, 20)
    page = request.GET.get('page')
    customers = paginator.get_page(page)

    return render(request, 'billing.html', {'customers': customers})


def get_sales_report(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            orders = Order.objects.filter(created_at__range=(start_datetime, end_datetime))
        else:
            orders = Order.objects.filter().order_by('-pk')[:10]
    else:
        orders = Order.objects.filter().order_by('-pk')[:10]

    return render(request, 'get-sales-report.html', {'orders': orders})


def export_report_to_csv(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    if start_date_str and end_date_str:
        start_datetime = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date_str, '%Y-%m-%d')
        orders = Order.objects.filter(created_at__range=(start_datetime, end_datetime)).order_by('pk')
    else:
        orders = Order.objects.all().order_by('pk')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="orders-{start_date_str}-{end_date_str}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Invoice No.', 'Invoice Date', 'Customer', 'GSTIN', 'Order Total(MRP)', 'Discount %',
                     'Order Total(S.P.)(Customer)', 'GAP', 'Order Total(S.P.)(Super Market)', 'Super Market CGST',
                     'Super Market SGST', 'Super Market GST Total', 'Super Market Order Total', 'GAP',
                     'Order Total(S.P.)(Franchise)', 'Franchise CGST', 'Franchise SGST', 'Franchise GST Total',
                     'Franchise Order Total', 'Payment Status', 'Payment Type'])

    for order in orders:
        if order.customer.order_type == 'super market':
            writer.writerow(
                [order.id, order.created_at.strftime('%Y-%m-%d %H:%M:%S'), order.customer, order.customer.gstin,
                 f'₹{order.real_order_total()}', '-', '-', '-', f'₹{order.store_order_total():.2f}',
                 f'₹{order.store_sgst():.2f}', f'₹{order.store_sgst():.2f}', f'₹{order.store_gst():.2f}',
                 f'₹{order.store_cgst_total():.2f}', '-', '-', '-', '-', '-', '-',
                 f'{order.payment_status} ₹{order.store_cgst_total()}',
                 order.payment_type])

        elif order.customer.order_type == 'franchise':
            writer.writerow(
                [order.id, order.created_at.strftime('%Y-%m-%d %H:%M:%S'), order.customer, order.customer.gstin,
                 order.real_order_total(), '-', '-', '-', '-', '-', '-', '-', '-', '-',
                 f'₹{order.franchise_order_total():.2f}', f'₹{order.franchise_sgst():.2f}',
                 f'₹{order.franchise_sgst():.2f}', f'₹{order.franchise_gst():.2f}',
                 f'₹{order.franchise_cgst_total():.2f}',
                 f'{order.payment_status} ₹{order.franchise_cgst_total()}', order.payment_type])

        else:
            writer.writerow(
                [order.id, order.created_at.strftime('%Y-%m-%d %H:%M:%S'), order.customer, order.customer.gstin,
                 f'₹{order.real_order_total()}', f'''{order.discount}%''', f'₹{order.order_total}', '-', '-', '-', '-',
                 '-', '-',
                 '-', '-', '-', '-', '-', '-', f'{order.payment_status} ₹{order.order_total}', order.payment_type])

    return response


@login_required
def add_new_customer(request):
    form = CustomerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        customer = form.save(commit=False)
        if customer.order_type in ['franchise', 'super market']:
            customer.save()
            return redirect('customer_extended_form', customer_id=customer.pk)
        else:
            customer.save()
            return redirect('order_list', customer_id=customer.pk)
    return render(request, 'add_new_customer.html', {'form': form})


def customer_extended_form(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    form = CustomerProfileForm(request.POST or None, instance=customer)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('order_list', customer_id=customer.pk)
    else:
        form = CustomerProfileForm(request.POST or None, instance=customer)

    return render(request, 'customer_extended.html', {'form': form})


@login_required
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)

    if customer.order_type == 'normal':
        form1 = CustomerForm(instance=customer)
        form2 = None
    else:
        form1 = CustomerForm(instance=customer)
        form2 = CustomerProfileForm(instance=customer)

    if request.method == "POST":
        form1 = CustomerForm(request.POST, instance=customer)
        if form1.is_valid():
            form1.save()
            # Handle form submission

        if form2 is not None:
            form2 = CustomerProfileForm(request.POST, instance=customer)
            if form2.is_valid():
                form2.save()
                return redirect('order_list', customer_id=customer.pk)
        else:
            return redirect('order_list', customer_id=customer.pk)

    context = {
        'form1': form1,
        'form2': form2,
    }
    return render(request, 'edit-customer.html', context)


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
                                                  out_quantity=order_item.quantity,
                                                  invoice_number=order_id)
        quantity_object.save()
        order.order_total += order_item.quantity * product.price
        order.save()
        return redirect('order_detail', customer_id=customer.id, order_id=order.id)

    return render(request, 'order_detail.html',
                  {'form': form, 'customer': customer, 'order': order, 'order_items': order_items})


def order_paid_cash(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    if order.payment_status != 'Paid':
        order.payment_type = 'Cash'
        order.save()

        if customer.order_type == 'franchise':
            add_credit = Credit.objects.create(name=customer.name + f"""#{order_id}""",
                                               invoice_number=order_id,
                                               amount=order.franchise_cgst_total())
        elif customer.order_type == 'super market':
            add_credit = Credit.objects.create(name=customer.name + f"""#{order_id}""",
                                               invoice_number=order_id,
                                               amount=order.store_cgst_total())
        else:
            add_credit = Credit.objects.create(name=customer.name + f"""#{order_id}""",
                                               invoice_number=order_id,
                                               amount=order.order_total)
        add_credit.save()
        messages.success(request, 'The Order is has been Paid')
    else:
        messages.error(request, 'The Order is Already Paid')
    return redirect('order_list', customer_id=customer.id)


def order_paid_upi(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)

    if order.payment_status != 'Paid':
        order.payment_status = 'Paid'
        order.payment_type = 'UPI'
        order.save()

        if customer.order_type == 'franchise':
            add_credit = Credit.objects.create(name=customer.name + f"""#{order_id}""",
                                               invoice_number=order_id,
                                               payment_type='UPI',
                                               amount=order.franchise_cgst_total())
        elif customer.order_type == 'super market':
            add_credit = Credit.objects.create(name=customer.name + f"""#{order_id}""",
                                               invoice_number=order_id,
                                               payment_type='UPI',
                                               amount=order.store_cgst_total())
        else:
            add_credit = Credit.objects.create(name=customer.name + f"""#{order_id}""",
                                               invoice_number=order_id,
                                               payment_type='UPI',
                                               amount=order.order_total)
        add_credit.save()
        messages.success(request, 'The Order is has been Paid')
        return redirect(edit_credit, credit_id=add_credit.id)
    else:
        messages.error(request, 'The Order is Already Paid')
        return redirect(order_list, customer_id=customer_id)


def order_paid_net(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)

    if order.payment_status != 'Paid':
        order.payment_status = 'Paid'
        order.payment_type = 'Bank Transfer'
        order.save()

        if customer.order_type == 'franchise':
            add_credit = Credit.objects.create(name=customer.name + f"""#{order_id}""",
                                               invoice_number=order_id,
                                               payment_type='Bank Transfer',
                                               amount=order.franchise_cgst_total())
        elif customer.order_type == 'super market':
            add_credit = Credit.objects.create(name=customer.name + f"""#{order_id}""",
                                               invoice_number=order_id,
                                               payment_type='Bank Transfer',
                                               amount=order.store_cgst_total())
        else:
            add_credit = Credit.objects.create(name=customer.name + f"""#{order_id}""",
                                               invoice_number=order_id,
                                               payment_type='Bank Transfer',
                                               amount=order.order_total)
        add_credit.save()
        messages.success(request, 'The Order is has been Paid')
        return redirect(edit_credit, credit_id=add_credit.id)
    else:
        messages.error(request, 'The Order is Already Paid')
        return redirect(order_list, customer_id=customer_id)


def order_dis_five(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    if order.payment_status != 'Paid':
        order.order_total = order.order_total - order.order_total * 5 / 100
        order.discount = 5
        order.save()
        messages.success(request, '5% Discount has been Applied')
    else:
        messages.error(request, 'You cannot apply discount on a paid order')

    return redirect('order_detail', customer_id=customer_id, order_id=order_id)


def order_dis_ten(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    if order.payment_status != 'Paid':
        order.order_total = order.order_total - order.order_total * 10 / 100
        order.discount = 10
        order.save()
        messages.success(request, '10% Discount has been Applied')
    else:
        messages.error(request, 'You cannot apply discount on a paid order')

    return redirect('order_detail', customer_id=customer_id, order_id=order_id)


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
    return render(request, 'order_item_edit.html',
                  {'form': form, 'customer': customer, 'order': order, 'order_item': order_item})


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
    return render(request, 'invoice_view.html',
                  {'order': order, 'customer': customer, 'order_items': order_items, 'total_amount': total_amount})
