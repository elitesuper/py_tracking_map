from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import connections
import json

# Create your views here.
@login_required
def index(request):
    with connections['trackdb'].cursor() as cursor:
        cursor.execute("SELECT * FROM track_table LIMIT 0, 10")
        rows = cursor.fetchall()

    print(rows)
    context = {
        'rows': json.dumps(rows),
    }
    return render(request, 'index.html', context)


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        next_url = request.POST.get('next') or request.GET.get('next', '/')
        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')