from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, Order, Product, OrderItem
from .forms import OrderForm, OrderItemForm, CustomerForm, CustomerProfileForm, DeliveryForm
from django.contrib.auth.decorators import login_required
from Stock.models import Quantity
from xhtml2pdf import pisa
from num2words import num2words
from django.template.loader import get_template
from django.contrib import messages
from Accounting.models import *
from Accounting.views import edit_credit
import csv
from django.http import HttpResponse
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.utils import timezone
import decimal


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


def get_gst_report(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            orders = Order.objects.filter(created_at__range=(start_datetime, end_datetime))
        else:
            orders = Order.objects.filter().order_by('-pk')[:100]
    else:
        orders = Order.objects.filter().order_by('-pk')[:100]

    # Calculate the sum of desired values
    total_real_order_total = sum(order.order_total for order in orders)
    total_cgst = sum(order.cgst() for order in orders)
    total_sgst = sum(order.sgst() for order in orders)
    total_total_gst = sum(order.total_gst() for order in orders)
    total_order_total_with_gst = sum(order.order_total_with_gst() for order in orders)

    return render(request, 'get-gst-report.html', {
        'orders': orders,
        'total_real_order_total': total_real_order_total,
        'total_cgst': total_cgst,
        'total_sgst': total_sgst,
        'total_total_gst': total_total_gst,
        'total_order_total_with_gst': total_order_total_with_gst
    })


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
    writer.writerow(['Invoice No.', 'Invoice Date', 'Party Name', 'GSTIN', 'Total(MRP)', 'CGST (6%)',
                     'SGST (6%)', 'Total Tax', 'Order Total', 'Tax Type', 'Type'])

    order_total_sum = 0
    cgst_sum = 0
    sgst_sum = 0
    total_gst_sum = 0
    order_total_with_gst_sum = 0

    for order in orders:
        if order.customer.order_type != 'normal':
            writer.writerow(
                [order.id, order.created_at.strftime('%Y-%m-%d'), order.customer, order.customer.gstin,
                 f'{order.order_total}', f'{order.cgst():.2f}', f'{order.sgst():.2f}',
                 f'{order.total_gst():.2f}', f'{order.order_total_with_gst():.2f}', 'CS GST', 'Taxable'])

            order_total_sum += order.order_total
            cgst_sum += order.cgst()
            sgst_sum += order.sgst()
            total_gst_sum += order.total_gst()
            order_total_with_gst_sum += order.order_total_with_gst()

    writer.writerow(['', '', '', '', '', '', '', '', '', '', ''])
    writer.writerow(['Total', '', '', '', f'{order_total_sum:.2f}', f'{cgst_sum:.2f}', f'{sgst_sum:.2f}',
                     f'{total_gst_sum:.2f}', f'₹{order_total_with_gst_sum:.2f}', '', ''])

    return response


@login_required
def get_sales_report(request):
    total_sales = Order.objects.aggregate(TOTAL=Sum('order_total'))['TOTAL']
    total_sales_with_gst = sum(order.order_total_with_gst() for order in Order.objects.all())
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            orders = Order.objects.filter(created_at__range=(start_datetime, end_datetime))
            total_sales = orders.aggregate(TOTAL=Sum('order_total'))['TOTAL']
            total_sales_with_gst = sum(order.order_total_with_gst() for order in orders)

        else:
            orders = Order.objects.filter().order_by('-pk')
    else:
        orders = Order.objects.filter().order_by('-pk')

    return render(request, 'get_sales_report.html',
                  {'orders': orders, 'total_sales': total_sales, 'total_sales_with_gst': total_sales_with_gst})


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
    total_sales = orders.aggregate(TOTAL=Sum('order_total'))['TOTAL']
    gst_total = 0

    if total_sales is not None:
        gst_total = round(total_sales + total_sales * 12 / 100, 0)

    invoice_search = request.GET.get('invoice_search')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    message = ""

    if invoice_search and invoice_search.strip():
        orders = Order.objects.filter(Q(pk__icontains=invoice_search) & Q(customer=customer))

        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            orders = orders.filter(created_at__range=(start_datetime, end_datetime))
            message = f"Showing results of '{invoice_search}' from {start_date} to {end_date}"
        else:
            message = f"Showing results of '{invoice_search}'"
        total_sales = orders.aggregate(TOTAL=Sum('order_total'))['TOTAL']
        gst_total = round(total_sales + total_sales * 12 / 100, 0)
    else:
        if start_date and end_date:
            start_datetime = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_datetime = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            orders = orders.filter(created_at__range=(start_datetime, end_datetime))
            message = f"Showing results from {start_date} to {end_date}"
            total_sales = orders.aggregate(TOTAL=Sum('order_total'))['TOTAL']
            gst_total = round(total_sales + total_sales * 12 / 100, 0)

    form = OrderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        order = form.save(commit=False)
        order.customer = customer
        order_update = Customer.objects.get(id=customer_id)
        order_update.no_of_order = order_update.no_of_order + 1
        order_update.save()
        order.save()
        return redirect('order_detail', customer_id=customer.id, order_id=order.id)

    context = {
        'customer': customer,
        'orders': orders,
        'form': form,
        'total_sales': total_sales,
        'message': message,
        'gst_total': gst_total,
    }
    return render(request, 'order_list.html', context=context)


def order_delete(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)

    # Delete the order
    customer_orders = customer.no_of_order - 1
    customer.no_of_order = customer_orders
    customer.save()
    order.delete()

    return redirect('order_list', customer_id=customer.id)


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
        if customer.order_type == 'franchise':
            order.order_total = round(order.order_total + order_item.quantity * product.franchise_price, 0)
            order.save()
        elif customer.order_type == 'super market':
            order.order_total = round(order.order_total + order_item.quantity * product.store_price, 0)
            order.save()
        else:
            order.order_total = round(order.order_total + order_item.quantity * product.price, 0)
            order.save()
        return redirect('order_detail', customer_id=customer.id, order_id=order.id)

    delivery_form = DeliveryForm(request.POST or None)
    if delivery_form.is_valid():
        order.delivery = delivery_form.cleaned_data['delivery']
        order.save()
        messages.success(request, f'Rs.{order.delivery} of Delivery Charges have been successfully added!')
        return redirect('order_detail', customer_id=customer.id, order_id=order.id)

    return render(request, 'order_detail.html',
                  {'form': form, 'customer': customer, 'order': order, 'order_items': order_items,
                   'delivery_form': delivery_form})


def order_paid_cash(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    if order.payment_status != 'Paid':
        order.payment_type = 'Cash'
        order.save()

        if customer.order_type != 'normal':
            add_credit = Credit.objects.create(name=customer.name + f"#{order_id}", invoice_number=order_id,
                                               date=datetime.now().date(), payment_type='Cash',
                                               amount=order.order_total_with_gst())
        else:
            add_credit = Credit.objects.create(name=customer.name + f"#{order_id}", invoice_number=order_id,
                                               date=datetime.now().date(), amount=order.order_total,
                                               payment_type='Cash')

        add_credit.save()
        messages.success(request, 'The Order is has been Paid')

        if order.delivery:
            debit_instance = get_object_or_404(Debit, name='Delivery Charges')
            add_debit = SubDebit.objects.create(name=f'{customer.name} - {order.id} delivery Charges',
                                                amount=order.delivery, date=datetime.now().date(),
                                                debit=debit_instance)
            add_debit.save()
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

        if customer.order_type != 'normal':
            add_credit = Credit.objects.create(name=customer.name + f"#{order_id}", invoice_number=order_id,
                                               date=datetime.now().date(), payment_type='UPI',
                                               amount=order.order_total_with_gst())
        else:
            add_credit = Credit.objects.create(name=customer.name + f"#{order_id}", invoice_number=order_id,
                                               date=datetime.now().date(), amount=order.order_total,
                                               payment_type='UPI')

        add_credit.save()
        messages.success(request, 'The Order is has been Paid')

        if order.delivery:
            debit_instance = get_object_or_404(Debit, name='Delivery Charges')
            add_debit = SubDebit.objects.create(name=f'{customer.name} - {order.id} delivery Charges',
                                                amount=order.delivery, date=datetime.now().date(),
                                                debit=debit_instance)
            add_debit.save()
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

        if customer.order_type != 'normal':
            add_credit = Credit.objects.create(name=customer.name + f"#{order_id}", invoice_number=order_id,
                                               date=datetime.now().date(), payment_type='Net Banking',
                                               amount=order.order_total_with_gst())
        else:
            add_credit = Credit.objects.create(name=customer.name + f"#{order_id}", invoice_number=order_id,
                                               date=datetime.now().date(), amount=order.order_total,
                                               payment_type='Net Banking')

        add_credit.save()
        messages.success(request, 'The Order is has been Paid')

        if order.delivery:
            debit_instance = get_object_or_404(Debit, name='Delivery Charges')
            add_debit = SubDebit.objects.create(name=f'{customer.name} - {order.id} delivery Charges',
                                                amount=order.delivery, date=datetime.now().date(),
                                                debit=debit_instance)
            add_debit.save()
        return redirect(edit_credit, credit_id=add_credit.id)
    else:
        messages.error(request, 'The Order is Already Paid')
        return redirect(order_list, customer_id=customer_id)


def order_paid_cheque(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)

    if order.payment_status != 'Paid':
        order.payment_status = 'Paid'
        order.payment_type = 'Cheque'
        order.save()

        if customer.order_type != 'normal':
            add_credit = Credit.objects.create(name=customer.name + f"#{order_id}", invoice_number=order_id,
                                               date=datetime.now().date(), payment_type='Cheque',
                                               amount=order.order_total_with_gst())
        else:
            add_credit = Credit.objects.create(name=customer.name + f"#{order_id}", invoice_number=order_id,
                                               date=datetime.now().date(), amount=order.order_total,
                                               payment_type='Cheque')

        add_credit.save()
        messages.success(request, 'The Order is has been Paid')

        if order.delivery:
            debit_instance = get_object_or_404(Debit, name='Delivery Charges')
            add_debit = SubDebit.objects.create(name=f'{customer.name} - {order.id} delivery Charges',
                                                amount=order.delivery, date=datetime.now().date(),
                                                debit=debit_instance)
            add_debit.save()
        return redirect(edit_credit, credit_id=add_credit.id)
    else:
        messages.error(request, 'The Order is Already Paid')
        return redirect(order_list, customer_id=customer_id)


def order_dis_five(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    if order.payment_status != 'Paid' and order.discount == 0:
        order.order_total = round(order.order_total - order.order_total * 5 / 100, 0)
        order.discount = 5
        order.save()
        messages.success(request, '5% Discount has been Applied')
    else:
        messages.error(request, "You cannot apply discount because it's already applied or the order is Paid")

    return redirect('order_detail', customer_id=customer_id, order_id=order_id)


def order_dis_ten(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    if order.payment_status != 'Paid' and order.discount == 0:
        order.order_total = round(order.order_total - order.order_total * 10 / 100, 0)
        order.discount = 10
        order.save()
        messages.success(request, '10% Discount has been Applied')
    else:
        messages.error(request, "You cannot apply discount because it's already applied or the order is Paid")

    return redirect('order_detail', customer_id=customer_id, order_id=order_id)


def order_dis_twenty(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    if order.payment_status != 'Paid' and order.discount == 0:
        order.order_total = round(order.order_total - order.order_total * 20 / 100, 0)
        order.discount = 20
        order.save()
        messages.success(request, '20% Discount has been Applied')
    else:
        messages.error(request, "You cannot apply discount because it's already applied or the order is Paid")

    return redirect('order_detail', customer_id=customer_id, order_id=order_id)


def order_dis_twenty_five(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    if order.payment_status != 'Paid' and order.discount == 0:
        order.order_total = round(order.order_total - order.order_total * 25 / 100, 0)
        order.discount = 25
        order.save()
        messages.success(request, '25% Discount has been Applied')
    else:
        messages.error(request, "You cannot apply discount because it's already applied or the order is Paid")

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
            if customer.order_type == 'franchise':
                order.order_total = round(order.order_total + product.franchise_price * diff)
            elif customer.order_type == 'super market':
                order.order_total = round(order.order_total + product.store_price * diff)
            else:
                order.order_total = round(order.order_total + product.price * diff)
        else:
            diff = old_quantity - new_order_item.quantity
            product.stock += diff
            if customer.order_type == 'franchise':
                order.order_total = round(order.order_total - product.franchise_price * diff)
            elif customer.order_type == 'super market':
                order.order_total = round(order.order_total - product.store_price * diff)
            else:
                order.order_total = round(order.order_total - product.price * diff)
        product.save()
        new_order_item.save()
        order.save()
        messages.success(request, f'{product.stock}, {diff}, {order.order_total}')
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
    total_amount_in_words_gst = num2words(order.order_total_with_gst())
    total_amount_in_words_normal = num2words(order.normal_order_total())
    total_amount_in_words_exhibition = num2words(order.normal_order_total())

    # Render the HTML template
    template = get_template('invoice.html')
    context = {'order': order, 'customer': customer, 'order_items': order_items, 'total_amount': total_amount,
               'total_amount_in_words_gst': total_amount_in_words_gst,
               'total_amount_in_words_normal': total_amount_in_words_normal,
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


def ledger_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    orders = Order.objects.filter(customer=customer)

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

        orders = orders.filter(created_at__range=(start_datetime, end_datetime))

    pending_orders = orders.filter(payment_status='Pending')
    paid_orders = orders.filter(payment_status='Paid')

    pending_total = pending_orders.aggregate(total_pending=Sum('order_total'))['total_pending']
    paid_total = paid_orders.aggregate(total_paid=Sum('order_total'))['total_paid']

    diff = 0
    if pending_total is not None and paid_total is not None:
        diff = paid_total - pending_total

    context = {
        'customer': customer,
        'pending_orders': pending_orders,
        'paid_orders': paid_orders,
        'pending_total': pending_total,
        'paid_total': paid_total,
        'diff': diff,
    }
    return render(request, 'ledger_view.html', context=context)
