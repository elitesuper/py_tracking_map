from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from app.forms import UserRegistrationForm, LoginForm
from app.models import User

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                next_url = request.POST.get('next') or request.GET.get('next', '/')
                login(request, user)
                return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    if request.method == 'GET':
        logout(request)
        return redirect('/login/')

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})