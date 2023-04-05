from django.shortcuts import render, redirect
from .models import Product, Quantity
from .forms import ProductForm, QuantityForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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
    product = Product.objects.get(code=code)
    stock = Quantity.objects.filter(product_code=product)

    stock_search = request.GET.get('stock_search')
    if stock_search != '' and stock_search is not None:
        stock = Quantity.objects.filter(product_code=code, date__day=stock_search)

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
        return redirect(edit_product_view, code=code)
    return render(request, 'edit_product.html', {'form': form, 'product': product, 'stock': stock})