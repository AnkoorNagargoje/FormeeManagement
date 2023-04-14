from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

@login_required
def accounting(request):
    credits = Credit.objects.all().order_by('-id')
    debits = Debit.objects.all().order_by('-id')

    credit_search = request.GET.get('credit_search')
    if credit_search != '' and credit_search is not None:
        credits = Credit.objects.filter(name__icontains=credit_search)

    debit_search = request.GET.get('debit_search')
    if debit_search != '' and debit_search is not None:
        debits = Debit.objects.filter(name__icontains=debit_search)

    total = Credit.objects.aggregate(TOTAL=Sum('amount'))['TOTAL']

    context = {
        'credits': credits,
        'debits': debits,
        'total': total,
    }

    return render(request, 'accounting.html', context=context)


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
        return redirect(accounting)
    else:
        form = CreditForm(instance=credit)

    return render(request, 'edit_credit.html', {'form': form, 'credit': credit})


@login_required
def edit_debit(request, debit_id):
    debit = Debit.objects.get(id=debit_id)
    form = DebitForm(request.POST or None, instance=debit)
    if form.is_valid():
        form.save()
        redirect(accounting)
    else:
        form = DebitForm(instance=debit)

    return render(request, 'edit_debit.html', {'form': form, 'debit': debit})