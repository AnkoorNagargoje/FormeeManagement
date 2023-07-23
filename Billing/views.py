from .models import Customer, Order, Product, OrderItem
from .forms import *
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
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum, Value, CharField, F, ExpressionWrapper, FloatField, Case, When, Q
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.db.models.functions import Cast
from django.db.models.functions import Round


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
            orders = Order.objects.filter().order_by('-created_at')[:100]
    else:
        orders = Order.objects.filter().order_by('-created_at')[:100]

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
    order_types = request.GET.getlist('order_type[]')
    payment_statuses = request.GET.getlist('payment_status[]')
    payment_types = ['Cash', 'UPI', 'Cheque', 'Net Banking']  # Available payment types

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    orders = Order.objects.all()

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        orders = orders.filter(created_at__range=(start_datetime, end_datetime))

    if order_types:
        orders = orders.filter(customer__order_type__in=order_types)

    if payment_statuses:
        orders = orders.filter(payment_status__in=payment_statuses)

    if 'payment_type' in request.GET:
        payment_type = request.GET.get('payment_type')
        if payment_type in payment_types:
            orders = orders.filter(payment_type=payment_type)

    total_sales = orders.aggregate(TOTAL=Sum('order_total'))['TOTAL']
    total_sales_with_gst = sum(order.order_total_with_gst() for order in orders)

    return render(request, 'get_sales_report.html', {
        'orders': orders,
        'total_sales': total_sales,
        'total_sales_with_gst': total_sales_with_gst,
        'payment_types': payment_types
    })


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
    sales_returns = SalesReturn.objects.filter(customer=customer, order__in=orders)
    return_items = ReturnItem.objects.filter(sales_return__in=sales_returns)

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
        'sales_returns': sales_returns,
        'return_items': return_items,
    }
    return render(request, 'order_list.html', context=context)


def order_delete(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)

    customer.save()
    order.delete()

    return redirect('order_list', customer_id=customer.id)


@login_required
def order_detail(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    order_items = order.orderitem_set.all()

    try:
        sales_return = SalesReturn.objects.get(order=order, customer=customer)
    except SalesReturn.DoesNotExist:
        sales_return = None

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
            order.order_total = round(order.order_total + order_item.quantity * product.franchise_price, 2)
            order.save()
        elif customer.order_type == 'super market':
            order.order_total = round(order.order_total + order_item.quantity * product.store_price, 2)
            order.save()
        else:
            order.order_total = round(order.order_total + order_item.quantity * product.price, 2)
            order.save()
        return redirect('order_detail', customer_id=customer.id, order_id=order.id)

    delivery_form = DeliveryForm(request.POST or None)
    if delivery_form.is_valid():
        if delivery_form.cleaned_data['delivery']:
            order.delivery = delivery_form.cleaned_data['delivery']
            messages.success(request, f'{order.delivery} Delivery Charges have been successfully added!')

        if delivery_form.cleaned_data['discount']:
            if order.payment_status != 'Paid' and order.discount == 0:
                order.discount = delivery_form.cleaned_data['discount']
                order.order_total = round(order.order_total - order.order_total * order.discount / 100, 0)
                order.save()
                messages.success(request, f'{order.discount}% Discount has been Applied')
            else:
                messages.error(request, "You cannot apply discount because it's already applied or the order is Paid")
        order.save()
        return redirect('order_detail', customer_id=customer.id, order_id=order.id)

    return render(request, 'order_detail.html',
                  {'form': form, 'customer': customer, 'order': order, 'order_items': order_items,
                   'delivery_form': delivery_form, 'sales_return': sales_return})


def register_sales_return(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)

    if request.method == 'POST':
        add_sales_return = SalesReturn.objects.create(customer=customer, order=order)
        add_sales_return.save()

        return redirect('returned_items', customer_id=customer_id, order_id=order_id,
                        sales_return_id=add_sales_return.id)


def returned_items(request, customer_id, order_id, sales_return_id):
    customer = get_object_or_404(Customer, id=customer_id)
    sales_order = get_object_or_404(Order, id=order_id, customer=customer)
    sales_return = get_object_or_404(SalesReturn, id=sales_return_id)
    order_items = sales_return.returnitem_set.all()

    if request.method == 'POST':
        returned_item_form = ReturnedItemForm(order_id=order_id, data=request.POST)

        if returned_item_form.is_valid():
            returned_item = returned_item_form.save(commit=False)
            returned_item.sales_return = sales_return
            if sales_return.customer.order_type == 'franchise':
                returned_item.return_total = round(
                    returned_item.return_total + returned_item.quantity * returned_item.product.product.franchise_price,
                    2)
                returned_item.save()
            if sales_return.customer.order_type == 'super market':
                returned_item.return_total = round(
                    returned_item.return_total + returned_item.quantity * returned_item.product.product.store_price, 2)
                returned_item.save()
            if sales_return.customer.order_type == 'normal':
                returned_item.return_total = round(
                    returned_item.return_total + returned_item.quantity * returned_item.product.product.price, 2)
                returned_item.save()

            returned_item.save()

            return redirect('returned_items', customer_id=customer_id, order_id=order_id,
                            sales_return_id=sales_return.id)

    else:
        returned_item_form = ReturnedItemForm(order_id=order_id)
    context = {
        'sales_return': sales_return,
        'order': sales_order,
        'order_items': order_items,
        'form': returned_item_form,
    }

    return render(request, 'returned_items.html', context)


def order_paid_cash(request, customer_id, order_id):
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(Order, id=order_id, customer=customer)
    if order.payment_status != 'Paid':
        order.payment_type = 'Cash'
        order.save()

        if customer.order_type != 'normal':
            add_credit = Credit.objects.create(name=customer.name, invoice_number=order_id,
                                               date=datetime.now().date(), payment_type='Cash',
                                               amount=order.order_total_with_gst())
        else:
            add_credit = Credit.objects.create(name=customer.name, invoice_number=order_id,
                                               date=datetime.now().date(), amount=order.order_total,
                                               payment_type='Cash')

        add_credit.save()
        messages.success(request, 'The Order is has been Paid')

        if order.delivery:
            debit_instance = get_object_or_404(Debit, name='Delivery Charges')
            add_debit = SubDebit.objects.create(name=f'{customer.name} - {order.id} delivery Charges',
                                                sub_amount=order.delivery, amount=order.delivery,
                                                date=datetime.now().date(),
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
            add_credit = Credit.objects.create(name=customer.name, invoice_number=order_id,
                                               date=datetime.now().date(), payment_type='UPI',
                                               amount=order.order_total_with_gst())
        else:
            add_credit = Credit.objects.create(name=customer.name, invoice_number=order_id,
                                               date=datetime.now().date(), amount=order.order_total,
                                               payment_type='UPI')

        add_credit.save()
        messages.success(request, 'The Order is has been Paid')

        if order.delivery:
            debit_instance = get_object_or_404(Debit, name='Delivery Charges')
            add_debit = SubDebit.objects.create(name=f'{customer.name} - {order.id} delivery Charges',
                                                sub_amount=order.delivery, amount=order.delivery,
                                                date=datetime.now().date(),
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
            add_credit = Credit.objects.create(name=customer.name, invoice_number=order_id,
                                               date=datetime.now().date(), payment_type='Net Banking',
                                               amount=order.order_total_with_gst())
        else:
            add_credit = Credit.objects.create(name=customer.name, invoice_number=order_id,
                                               date=datetime.now().date(), amount=order.order_total,
                                               payment_type='Net Banking')

        add_credit.save()
        messages.success(request, 'The Order is has been Paid')

        if order.delivery:
            debit_instance = get_object_or_404(Debit, name='Delivery Charges')
            add_debit = SubDebit.objects.create(name=f'{customer.name} - {order.id} delivery Charges',
                                                sub_amount=order.delivery, amount=order.delivery,
                                                date=datetime.now().date(),
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
            add_credit = Credit.objects.create(name=customer.name, invoice_number=order_id,
                                               date=datetime.now().date(), payment_type='Cheque',
                                               amount=order.order_total_with_gst())
        else:
            add_credit = Credit.objects.create(name=customer.name, invoice_number=order_id,
                                               date=datetime.now().date(), amount=order.order_total,
                                               payment_type='Cheque')

        add_credit.save()
        messages.success(request, 'The Order is has been Paid')

        if order.delivery:
            debit_instance = get_object_or_404(Debit, name='Delivery Charges')
            add_debit = SubDebit.objects.create(name=f'{customer.name} - {order.id} delivery Charges',
                                                sub_amount=order.delivery, amount=order.delivery,
                                                date=datetime.now().date(),
                                                debit=debit_instance)
            add_debit.save()
        return redirect(edit_credit, credit_id=add_credit.id)
    else:
        messages.error(request, 'The Order is Already Paid')
        return redirect(order_list, customer_id=customer_id)


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

    if customer.order_type == 'franchise':
        order.order_total -= order_item.product.franchise_price * order_item.quantity
    elif customer.order_type == 'super market':
        order.order_total -= order_item.product.store_price * order_item.quantity
    else:
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
        return redirect('generate_ledger', customer_id=customer_id, start_date=start_date, end_date=end_date)

    orders_and_credit = (
        orders.annotate(
            item_type=Value('order', output_field=CharField()),
            item_invoice_number=Cast('id', output_field=CharField()),
            item_created_at=F('created_at'),
            item_total=Case(
                When(customer__order_type='normal', then=Round(F('order_total'), 0)),
                default=Round(F('order_total') + F('order_total') * 0.12, 0),
                # Calculate order total with GST and round off
                output_field=FloatField()
            ),
            item_payment_status=F('payment_status'),
            item_payment_type=F('payment_type'),
            item_primary_key=F('pk')  # Add primary key field
        )
        .values('item_type', 'item_invoice_number', 'item_created_at', 'item_total', 'item_payment_status',
                'item_payment_type', 'item_primary_key')  # Include primary key field
    )

    credits = (
        Credit.objects.filter(invoice_number__in=orders.values_list('id', flat=True))
        .annotate(
            item_type=Value('credit', output_field=CharField()),
            item_invoice_number=Cast('invoice_number', output_field=CharField()),
            item_created_at=F('date'),
            item_total=F('amount'),
            item_payment_status=Value('Paid', output_field=CharField()),
            item_payment_type=F('payment_type'),
            item_primary_key=F('pk')  # Add primary key field
        )
        .values('item_type', 'item_invoice_number', 'item_created_at', 'item_total', 'item_payment_status',
                'item_payment_type', 'item_primary_key')  # Include primary key field
    )

    orders_and_credit = orders_and_credit.union(credits).order_by('item_created_at')

    sum_orders = orders.aggregate(total_pending=Sum(
        Case(
            When(customer__order_type='normal', then=F('order_total')),
            default=ExpressionWrapper(
                F('order_total') + F('order_total') * 0.12,  # Calculate order total with GST
                output_field=FloatField()
            ),
            output_field=FloatField()
        )
    ))['total_pending'] or 0.0

    paid_total = orders.filter(payment_status='Paid').aggregate(total_paid=Sum(
        Case(
            When(customer__order_type='normal', then=F('order_total')),
            default=ExpressionWrapper(
                F('order_total') + F('order_total') * 0.12,  # Calculate order total with GST
                output_field=FloatField()
            ),
            output_field=FloatField()
        )
    ))['total_paid'] or 0.0

    diff = round(sum_orders - paid_total, 0)
    diff_words = num2words(diff)

    context = {
        'customer': customer,
        'orders': orders_and_credit,
        'sum_orders': sum_orders,
        'paid_total': paid_total,
        'diff': diff,
        'diff_words': diff_words,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'ledger_view.html', context=context)


def generate_ledger(request, customer_id, start_date, end_date):
    customer = get_object_or_404(Customer, id=customer_id)
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
    orders = Order.objects.filter(customer=customer, created_at__range=(start_datetime, end_datetime))

    orders_and_credit = (
        orders.annotate(
            item_type=Value('order', output_field=CharField()),
            item_invoice_number=Cast('id', output_field=CharField()),
            item_created_at=F('created_at'),
            item_total=Case(
                When(customer__order_type='normal', then=F('order_total')),
                default=ExpressionWrapper(
                    F('order_total') + F('order_total') * 0.12,  # Calculate order total with GST
                    output_field=FloatField()
                ),
                output_field=FloatField()
            ),
            item_payment_status=F('payment_status'),
            item_payment_type=F('payment_type')
        )
        .values('item_type', 'item_invoice_number', 'item_created_at', 'item_total', 'item_payment_status',
                'item_payment_type')
    )

    credits = (
        Credit.objects.filter(invoice_number__in=orders.values_list('id', flat=True))
        .annotate(
            item_type=Value('credit', output_field=CharField()),
            item_invoice_number=Cast('invoice_number', output_field=CharField()),
            item_created_at=F('date'),
            item_total=F('amount'),
            item_payment_status=Value('Paid', output_field=CharField()),
            item_payment_type=F('payment_type')
        )
        .values('item_type', 'item_invoice_number', 'item_created_at', 'item_total', 'item_payment_status',
                'item_payment_type')
    )

    orders_and_credit = orders_and_credit.union(credits).order_by('item_created_at')

    sum_orders = orders.aggregate(total_pending=Sum(
        Case(
            When(customer__order_type='normal', then=F('order_total')),
            default=ExpressionWrapper(
                F('order_total') + F('order_total') * 0.12,  # Calculate order total with GST
                output_field=FloatField()
            ),
            output_field=FloatField()
        )
    ))['total_pending'] or 0.0

    paid_total = orders.filter(payment_status='Paid').aggregate(total_paid=Sum(
        Case(
            When(customer__order_type='normal', then=F('order_total')),
            default=ExpressionWrapper(
                F('order_total') + F('order_total') * 0.12,  # Calculate order total with GST
                output_field=FloatField()
            ),
            output_field=FloatField()
        )
    ))['total_paid'] or 0.0

    diff = round(sum_orders - paid_total, 0)
    diff_words = num2words(diff)

    template = get_template('ledger.html')
    context = {
        'customer': customer,
        'orders': orders_and_credit,
        'sum_orders': sum_orders,
        'paid_total': paid_total,
        'diff': diff,
        'diff_words': diff_words,
        'start_date': start_date,
        'end_date': end_date,
    }
    html = template.render(context)

    # Create a PDF file using xhtml2pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Ledger-{customer.name}-{start_date}.pdf'
    pisa.CreatePDF(html, dest=response, encoding='utf-8')

    return response
