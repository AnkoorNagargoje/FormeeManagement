from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required


@login_required
def accounting(request):
    credits = Credit.objects.all()
    debits = Debit.objects.all()

    credit_search = request.GET.get('credit_search')
    if credit_search != '' and credit_search is not None:
        credits = Credit.objects.filter(name__icontains=credit_search)

    debit_search = request.GET.get('debit_search')
    if debit_search != '' and debit_search is not None:
        debits = Debit.objects.filter(name__icontains=debit_search)

    context = {
        'credits': credits,
        'debits': debits,
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
