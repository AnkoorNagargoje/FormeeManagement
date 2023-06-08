from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages
from django.db.models import Sum, DecimalField, ExpressionWrapper, F, Q, Case, When
from decimal import Decimal


@login_required
def accounting(request):
    return render(request, 'accounting.html')


from django.db.models import Sum, Q

from decimal import Decimal
from django.db.models import Sum, Q

def pnl(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Calculate total sales within the specified date range
    total_sales = Order.objects.filter(created_at__range=[start_date, end_date]).aggregate(TOTAL=Sum('order_total'))['TOTAL']
    total_sales = Decimal(total_sales or 0)

    direct_debit_types = DebitType.objects.filter(type='direct')
    direct_debits = Debit.objects.filter(debit_type__in=direct_debit_types)
    direct_subdebit_total = SubDebit.objects.filter(debit__in=direct_debits, date__range=[start_date, end_date]).aggregate(total_sum=Sum('amount'))['total_sum']
    direct_subdebit_total = Decimal(direct_subdebit_total or 0)

    indirect_debit_types = DebitType.objects.filter(type='indirect')
    indirect_debits = Debit.objects.filter(debit_type__in=indirect_debit_types)
    indirect_subdebit_total = SubDebit.objects.filter(debit__in=indirect_debits, date__range=[start_date, end_date]).aggregate(total_sum=Sum('amount'))['total_sum']
    indirect_subdebit_total = Decimal(indirect_subdebit_total or 0)

    miscellaneous_debit_types = DebitType.objects.filter(type='miscellaneous')
    miscellaneous_debits = Debit.objects.filter(debit_type__in=miscellaneous_debit_types)
    miscellaneous_subdebit_total = SubDebit.objects.filter(debit__in=miscellaneous_debits, date__range=[start_date, end_date]).aggregate(total_sum=Sum('amount'))['total_sum']
    miscellaneous_subdebit_total = Decimal(miscellaneous_subdebit_total or 0)

    total_sum_of_subdebits = direct_subdebit_total + indirect_subdebit_total + miscellaneous_subdebit_total

    pnl = total_sales - total_sum_of_subdebits
    x = 'Profit' if pnl > 0 else 'Loss'

    context = {
        'total_sales': total_sales,
        'pnl': pnl,
        'x': x,
        'direct_total': direct_subdebit_total,
        'indirect_total': indirect_subdebit_total,
        'miscellaneous_total': miscellaneous_subdebit_total,
        'total_sum_of_subdebits': total_sum_of_subdebits,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'pnl.html', context=context)




@login_required
def credits_view(request):
    credit_types = dict(CREDIT_TYPE)  # Convert CREDIT_TYPE tuple to a dictionary for display purposes

    credit_sums = {}
    total_credit_sum = 0

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    credits = Credit.objects.all()

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

        credits = credits.filter(date__range=(start_datetime, end_datetime))

    for credit_type, _ in CREDIT_TYPE:
        credit_sum = credits.filter(credit_type=credit_type).aggregate(total_credit=Sum('amount'))
        credit_sums[credit_type] = credit_sum['total_credit'] or 0

    total_credit_sum = credits.aggregate(total_credit_sum=Sum('amount'))['total_credit_sum'] or 0

    # Convert credit_sums dictionary to a list of tuples
    credit_sums = [(credit_type, credit_sums.get(credit_type, 0)) for credit_type in credit_types.keys()]

    context = {
        'credit_types': credit_types,
        'credit_sums': credit_sums,
        'total_credit_sum': total_credit_sum,
    }
    return render(request, 'credits_view.html', context)


@login_required
def credits_sales_view(request):
    credits = Credit.objects.filter(credit_type='sales').order_by('-id')[:10]
    total_credits = credits.aggregate(TOTAL=Sum('amount'))['TOTAL']

    credit_search = request.GET.get('credit_search')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    message = ""

    if credit_search and credit_search.strip():
        credits = credits.filter(name__icontains=credit_search)

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

            credits = credits.filter(date__range=(start_datetime, end_datetime))
            message = f"Showing results from {start_date} to {end_date}"
            total_credits = credits.aggregate(TOTAL=Sum('amount'))['TOTAL']

    total = Credit.objects.filter(credit_type='sales').aggregate(TOTAL=Sum('amount'))['TOTAL']

    context = {
        'credits': credits,
        'total': total,
        'total_credits': total_credits,
        'message': message,
    }

    return render(request, 'sales_view.html', context=context)


@login_required
def credits_indirect_view(request):
    credits = Credit.objects.filter(credit_type='indirect').order_by('-id')[:10]
    total_credits = credits.aggregate(TOTAL=Sum('amount'))['TOTAL']

    credit_search = request.GET.get('credit_search')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    message = ""

    if credit_search and credit_search.strip():
        credits = credits.filter(name__icontains=credit_search)

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

            credits = credits.filter(date__range=(start_datetime, end_datetime))
            message = f"Showing results from {start_date} to {end_date}"
            total_credits = credits.aggregate(TOTAL=Sum('amount'))['TOTAL']

    total = Credit.objects.filter(credit_type='indirect').aggregate(TOTAL=Sum('amount'))['TOTAL']

    context = {
        'credits': credits,
        'total': total,
        'total_credits': total_credits,
        'message': message,
    }

    return render(request, 'indirect_view.html', context=context)


@login_required
def credits_miscellaneous_view(request):
    credits = Credit.objects.filter(credit_type='miscellaneous').order_by('-id')[:10]
    total_credits = credits.aggregate(TOTAL=Sum('amount'))['TOTAL']

    credit_search = request.GET.get('credit_search')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    message = ""

    if credit_search and credit_search.strip():
        credits = credits.filter(name__icontains=credit_search)

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

            credits = credits.filter(date__range=(start_datetime, end_datetime))
            message = f"Showing results from {start_date} to {end_date}"
            total_credits = credits.aggregate(TOTAL=Sum('amount'))['TOTAL']

    total = Credit.objects.filter(credit_type='miscellaneous').aggregate(TOTAL=Sum('amount'))['TOTAL']

    context = {
        'credits': credits,
        'total': total,
        'total_credits': total_credits,
        'message': message,
    }

    return render(request, 'miscellaneous_view.html', context=context)


def debits_view(request):
    debit_types = dict(DebitType.TYPE_CHOICES)

    debit_sums = {}
    total_subdebit_sum = 0

    subdebit_start_date = request.GET.get('subdebit_start_date')
    subdebit_end_date = request.GET.get('subdebit_end_date')

    # Calculate the sum of all subdebits for the DebitType under 'direct,' 'indirect,' and 'miscellaneous'
    subdebit_sum = SubDebit.objects.filter(
        debit__debit_type__type__in=[DebitType.DIRECT, DebitType.INDIRECT, DebitType.MISCELLANEOUS])
    if subdebit_start_date and subdebit_end_date:
        subdebit_start_datetime = datetime.strptime(subdebit_start_date, '%Y-%m-%d')
        subdebit_end_datetime = datetime.strptime(subdebit_end_date, '%Y-%m-%d')
        subdebit_sum = subdebit_sum.filter(date__range=(subdebit_start_datetime, subdebit_end_datetime))

    subdebit_sum = subdebit_sum.aggregate(total_subdebit=Sum('amount'))
    total_subdebit_sum = subdebit_sum['total_subdebit'] or 0

    # Calculate the sum of subdebits for each DebitType
    subdebit_sums = {}
    for debit_type, _ in DebitType.TYPE_CHOICES:
        subdebit_sum = SubDebit.objects.filter(debit__debit_type__type=debit_type)
        if subdebit_start_date and subdebit_end_date:
            subdebit_sum = subdebit_sum.filter(date__range=(subdebit_start_datetime, subdebit_end_datetime))

        subdebit_sum = subdebit_sum.aggregate(total_subdebit=Sum('amount'))
        subdebit_sums[debit_type] = subdebit_sum['total_subdebit'] or 0

    # Convert debit_sums dictionary to a list of tuples
    debit_sums = [(debit_type, debit_sums.get(debit_type, 0)) for debit_type in debit_types.keys()]

    context = {
        'debit_types': debit_types,
        'debit_sums': debit_sums,
        'subdebit_sums': subdebit_sums,  # Add the subdebit sums to the context
        'total_subdebit_sum': total_subdebit_sum,
    }
    return render(request, 'debits_view.html', context)


@login_required
def debit_type_view(request, debit_type_param):
    debit_types = DebitType.objects.filter(type=debit_type_param)

    debits_with_total_amount = []

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    debits = Debit.objects.filter(debit_type__in=debit_types)  # Filter debits by debit types

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

        debits = debits.filter(subdebit__date__range=(start_datetime, end_datetime))

    for debit_type in debit_types:
        total_amount = debits.filter(debit_type=debit_type).aggregate(
            total_sum=Sum(ExpressionWrapper(F('subdebit__amount') / 1.0, output_field=DecimalField()))
        )['total_sum']
        debits_with_total_amount.append((debit_type, total_amount))

    total_amount_sum = sum(total_amount or Decimal(0) for _, total_amount in debits_with_total_amount)

    context = {
        'debits_with_total_amount': debits_with_total_amount,
        'debit_type': debit_type_param,
        'total_amount_sum': total_amount_sum,
    }

    return render(request, 'debit_type.html', context=context)


def add_debit_type_form(request, debit_type):
    form = DirectDebitTypeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        unsaved = form.save(commit=False)
        unsaved.type = debit_type
        unsaved.save()
        messages.success(request, 'Debit has been Successfully Added!')
        return redirect(debit_type_view, debit_type_param=debit_type)
    return render(request, 'add_debitType.html', {'form': form})


from django.db.models import Sum, DecimalField
from django.db.models import Q
from datetime import datetime


def debits_by_type_view(request, debit_type, debit_type_id):
    debit_type = DebitType.objects.get(type=debit_type, id=debit_type_id)

    debits = Debit.objects.filter(debit_type=debit_type)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        debits = debits.filter(subdebit__date__range=(start_datetime.date(), end_datetime.date()))

    debit_name = request.GET.get('debit_name')
    if debit_name:
        debits = debits.filter(Q(name__icontains=debit_name) | Q(subdebit__name__icontains=debit_name))

    debits = debits.annotate(
        sub_debit_sum=Sum('subdebit__amount', output_field=DecimalField())
    )

    grand_total_sum = debits.aggregate(total_sum=Sum('sub_debit_sum'))['total_sum'] or 0

    context = {
        'debit_type': debit_type,
        'debits': debits,
        'grand_total_sum': grand_total_sum,
    }
    return render(request, 'debits_by_type.html', context=context)


@login_required
def add_debits_form(request, debit_type, debit_type_id):
    debittype = DebitType.objects.get(type=debit_type, id=debit_type_id)
    form = DebitForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        unsaved = form.save(commit=False)
        unsaved.debit_type = debittype
        unsaved.save()
        messages.success(request, 'Debit has been Successfully Added!')
        return redirect(debits_by_type_view, debit_type=debit_type, debit_type_id=debit_type_id)
    return render(request, 'add_debit.html', {'form': form})


@login_required
def sub_debits_view(request, debit_type, debit_type_id, debit_id):
    debit_type_instance = DebitType.objects.get(type=debit_type, id=debit_type_id)
    debit = Debit.objects.get(id=debit_id)

    name_filter = request.GET.get('name')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    sub_debits = SubDebit.objects.filter(debit=debit)

    if name_filter:
        sub_debits = sub_debits.filter(name__icontains=name_filter)

    if start_date and end_date:
        sub_debits = sub_debits.filter(date__range=[start_date, end_date])

    total_amount = sub_debits.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    context = {
        'debit_type': debit_type_instance,
        'debit': debit,
        'sub_debits': sub_debits,
        'total_amount': total_amount,
    }

    return render(request, 'sub_debits.html', context)


@login_required
def add_subdebits_form(request, debit_type, debit_type_id, debit_id):
    debit_type_instance = DebitType.objects.get(type=debit_type, id=debit_type_id)
    debit = Debit.objects.get(id=debit_id)
    sub_debits = SubDebit.objects.filter(debit=debit)

    form = SubDebitForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        unsaved = form.save(commit=False)
        unsaved.debit = debit
        debit.amount += unsaved.amount
        unsaved.save()
        debit.save()
        messages.success(request, 'Debit has been Successfully Added!')
        return redirect(sub_debits_view, debit_type=debit_type, debit_type_id=debit_type_id, debit_id=debit_id)

    context = {
        'debit_type': debit_type_instance,
        'debit': debit,
        'sub_debits': sub_debits,
        'form': form,
    }
    return render(request, 'add_subdebit.html', context=context)


@login_required
def sub_debits_expand_view(request, debit_type, debit_type_id, debit_id, sub_debit_id):
    debit_type_instance = DebitType.objects.get(type=debit_type, id=debit_type_id)
    debit = Debit.objects.get(id=debit_id)
    subdebit = SubDebit.objects.filter(id=sub_debit_id)

    context = {
        'debit_type': debit_type_instance,
        'debit': debit,
        'subdebit': subdebit,
    }

    return render(request, 'sub_debit_expand.html', context=context)


@login_required
def total_expenses(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            debits = Debit.objects.filter(subdebit__date__range=(start_datetime, end_datetime)).annotate(
                total_subdebits=Sum('subdebit__amount'))
        else:
            debits = Debit.objects.annotate(total_subdebits=Sum('subdebit__amount'))
    else:
        debits = Debit.objects.annotate(total_subdebits=Sum('subdebit__amount'))

    total_sum_subdebits = debits.aggregate(total=Sum('total_subdebits'))['total']
    total_sum_subdebits = total_sum_subdebits or 0

    return render(request, 'debits.html', {'debits': debits, 'total_sum_subdebits': total_sum_subdebits})


@login_required
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
        messages.success(request, 'Credit has been Successfully Added!')
        return redirect(credits_sales_view)
    return render(request, 'add_credit.html', {'form': form})


@login_required
def add_debit(request):
    form = DebitForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Debit has been Successfully Added!')
        return redirect(debits_view)
    return render(request, 'add_debit.html', {'form': form})


@login_required
def edit_credit(request, credit_id):
    credit = Credit.objects.get(id=credit_id)
    form = CreditForm(request.POST or None, instance=credit)
    if form.is_valid():
        form.save()
        messages.success(request, 'Credit has been Successfully Added!')
        return redirect(credits_sales_view)
    else:
        form = CreditForm(instance=credit)

    return render(request, 'edit_credit.html', {'form': form, 'credit': credit})


@login_required
def edit_debit(request, debit_id):
    debit = Debit.objects.get(id=debit_id)
    form = DebitForm(request.POST or None, instance=debit)
    if form.is_valid():
        form.save()
        messages.success(request, 'Debit has been Successfully Added!')
        return redirect(debits_view)
    else:
        form = DebitForm(instance=debit)
        messages.error(request, f'Error while editing Debit! {form.errors}')

    return render(request, 'edit_debit.html', {'form': form, 'debit': debit})
