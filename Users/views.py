from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, authenticate
from django.contrib import messages
from django.contrib.auth import login, logout
from .forms import LoginForm


def login_request(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        cleandata = form.cleaned_data
        user = authenticate(username=cleandata['username'],
                            password=cleandata['password'])
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Username or Password Incorrect!')
            return redirect('/login/')

    return render(request, 'login.html', {'form': form})


def index_request(request):
    return render(request, 'index.html')


def logout_request(request):
    logout(request)
    return redirect('/')