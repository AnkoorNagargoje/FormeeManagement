from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Quantity
from .forms import ProductForm, QuantityForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime


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
    stock = Quantity.objects.all()

    stock = stock.exclude(in_quantity__isnull=True).order_by('-date')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        stock = stock.filter(date__range=(start_datetime, end_datetime))
    total_in_quantity_sum = stock.aggregate(total_sum=Sum('in_quantity'))['total_sum'] or 0

    context = {
        'stock': stock,
        'stock_sum': total_in_quantity_sum,
    }
    return render(request, 'stock_report.html', context=context)