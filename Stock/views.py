from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Quantity
from .forms import ProductForm, QuantityForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce


def home_view(request):
    return render(request, 'home.html')


@login_required
def stock_view(request):
    products = Product.objects.all().order_by('code')

    product_search = request.GET.get('product_search')
    if product_search != '' and product_search is not None:
        products = Product.objects.filter(name__icontains=product_search)

    return render(request, 'stock.html', {'products': products})


@login_required
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST or None)
        if form.is_valid():
            unsaved_form = form.save(commit=False)
            without_gst_price = unsaved_form.price * 100 / 112
            unsaved_form.franchise_price = without_gst_price - without_gst_price * 25 / 100
            unsaved_form.store_price = without_gst_price - without_gst_price * 20 / 100
            unsaved_form.save()
            return redirect('/stock/')
        else:
            messages.error(request, 'something is not correct')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@login_required
def edit_product_view(request, code):
    product = get_object_or_404(Product, code=code)

    # Initial stock queryset for the product
    stock = Quantity.objects.filter(product_code=product).order_by('-date')

    # Date filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        stock = stock.filter(date__range=(start_datetime, end_datetime))

    stock_search = request.GET.get('stock_search')
    if stock_search:
        try:
            stock_search = int(stock_search)
        except ValueError:
            error_message = "Please enter a valid Invoice Number."
            return render(request, 'edit_product.html',
                          {'product': product, 'stock': stock, 'error_message': error_message})

        stock = stock.filter(invoice_number=stock_search)

    form = QuantityForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        ipc = Product.objects.get(code=code)
        instance.product_code = ipc
        add_qty = instance.in_quantity
        sub_qty = instance.out_quantity
        if add_qty is not None:
            ipc.stock = ipc.stock + add_qty
        if sub_qty is not None:
            ipc.stock = ipc.stock - sub_qty
        ipc.save()
        instance.save()
        return redirect(stock_view)

    return render(request, 'edit_product.html', {'form': form, 'product': product, 'stock': stock})


@login_required
def stock_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    stock = Quantity.objects.all()

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        end_datetime = end_datetime.replace(hour=23, minute=59, second=59)  # Set end time to end of the day
        stock = stock.filter(date__range=(start_datetime, end_datetime))

    # Aggregate sums of in_quantity and out_quantity grouped by product
    aggregated_stock = stock.values('product_code__id', 'product_code__name', 'product_code__code').annotate(
        total_in_quantity=Coalesce(Sum('in_quantity'), Value(0)),
        total_out_quantity=Coalesce(Sum('out_quantity'), Value(0))
    )

    # Calculate the difference between total in and total out quantities for each product
    for item in aggregated_stock:
        item['difference'] = item['total_in_quantity'] - item['total_out_quantity']

    # Calculate the total sums and difference for all products
    total_in_quantity = aggregated_stock.aggregate(total_in_sum=Sum('total_in_quantity'))['total_in_sum']
    total_out_quantity = aggregated_stock.aggregate(total_out_sum=Sum('total_out_quantity'))['total_out_sum']
    total_difference = total_in_quantity - total_out_quantity

    context = {
        'stock': aggregated_stock,
        'total_in_quantity': total_in_quantity,
        'total_out_quantity': total_out_quantity,
        'total_difference': total_difference,
    }
    return render(request, 'stock_report.html', context=context)