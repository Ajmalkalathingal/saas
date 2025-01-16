from django.shortcuts import render,redirect
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login

# Create your views here.

def login_view(request):
    username = "admin"
    password = "admin"
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/')
    else:
        return render(request, 'auth/login.html')