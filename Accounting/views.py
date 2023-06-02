from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime
from django.contrib import messages


def accounting(request):
    return render(request, 'accounting.html')


def pnl(request):
    total_sales = Order.objects.aggregate(TOTAL=Sum('order_total'))['TOTAL']
    total_exp = Debit.objects.aggregate(TOTAL=Sum('amount'))['TOTAL']
    pnl = total_sales - total_exp
    x = ''

    if pnl > 0:
        x = 'Profit'
    else:
        x = 'Loss'

    context = {
        'total_sales': total_sales,
        'total_exp': total_exp,
        'pnl': pnl,
        'x': x,
    }

    return render(request, 'pnl.html', context=context)


@login_required
def credits_view(request):
    credits = Credit.objects.all().order_by('-id')[:10]
    total_credits = Credit.objects.aggregate(TOTAL=Sum('amount'))['TOTAL']

    credit_search = request.GET.get('credit_search')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    message = ""

    if credit_search and credit_search.strip():
        credits = Credit.objects.filter(name__icontains=credit_search)

        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            credits = credits.filter(date__range=(start_datetime, end_datetime))
            message = f"Showing results of '{credit_search}' from {start_date} to {end_date}"
        else:
            message = f"Showing results of '{credit_search}'"
        total_credits = credits.aggregate(TOTAL=Sum('amount'))['TOTAL']
    else:
        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            credits = Credit.objects.filter(date__range=(start_datetime, end_datetime))
            message = f"Showing results from {start_date} to {end_date}"
            total_credits = credits.aggregate(TOTAL=Sum('amount'))['TOTAL']

    total = Credit.objects.aggregate(TOTAL=Sum('amount'))['TOTAL']

    context = {
        'credits': credits,
        'total': total,
        'total_credits': total_credits,
        'message': message,
    }

    return render(request, 'credits_view.html', context=context)


@login_required
def debits_view(request):
    debits = Debit.objects.all().order_by('-id')[:10]
    total_debits = Debit.objects.aggregate(TOTAL=Sum('amount'))['TOTAL']

    debit_search = request.GET.get('credit_search')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    message = ""

    if debit_search and debit_search.strip():
        debits = Debit.objects.filter(name__icontains=debit_search)

        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            debits = debits.filter(date__range=(start_datetime, end_datetime))
            message = f"Showing results of '{debit_search}' from {start_date} to {end_date}"
        else:
            message = f"Showing results of '{debit_search}'"
        total_debits = debits.aggregate(TOTAL=Sum('amount'))['TOTAL']
    else:
        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            debits = Debit.objects.filter(date__range=(start_datetime, end_datetime))
            message = f"Showing results from {start_date} to {end_date}"
            total_debits = debits.aggregate(TOTAL=Sum('amount'))['TOTAL']

    total = Debit.objects.aggregate(TOTAL=Sum('amount'))['TOTAL']

    context = {
        'debits': debits,
        'total': total,
        'total_debits': total_debits,
        'message': message,
    }

    return render(request, 'debits_view.html', context=context)


def total_expenses(request):
    debits = Debit.objects.all()
    return render(request, 'debits.html', {'debits': debits})


def sales(request):
    total_sales = Order.objects.aggregate(TOTAL=Sum('order_total'))['TOTAL']
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            orders = Order.objects.filter(created_at__range=(start_datetime, end_datetime))
            total_sales = orders.aggregate(TOTAL=Sum('order_total'))['TOTAL']

        else:
            orders = Order.objects.filter().order_by('-pk')[:20]
    else:
        orders = Order.objects.filter().order_by('-pk')[:20]

    return render(request, 'sales.html', {'orders': orders, 'total_sales': total_sales})


@login_required
def add_credit(request):
    form = CreditForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(accounting)
    return render(request, 'add_credit.html', {'form': form})


@login_required
def add_debit(request):
    form = DebitForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(accounting)
    return render(request, 'add_debit.html', {'form': form})


@login_required
def edit_credit(request, credit_id):
    credit = Credit.objects.get(id=credit_id)
    form = CreditForm(request.POST or None, instance=credit)
    if form.is_valid():
        form.save()
        return redirect(credits_view)
    else:
        form = CreditForm(instance=credit)

    return render(request, 'edit_credit.html', {'form': form, 'credit': credit})


@login_required
def edit_debit(request, debit_id):
    debit = Debit.objects.get(id=debit_id)
    form = DebitForm(request.POST or None, instance=debit)
    if form.is_valid():
        form.save()
        return redirect(debits_view)
    else:
        form = DebitForm(instance=debit)
        messages.error(request, 'There is an error!')

    return render(request, 'edit_debit.html', {'form': form, 'debit': debit})
