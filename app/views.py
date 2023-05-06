from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from django.http import JsonResponse
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

@csrf_exempt
def get_data(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw'), 0)
        start = int(request.POST.get('start'), 0)
        length = int(request.POST.get('length'), 10)
    with connections['trackdb'].cursor() as cursor:
        # Modify the query to use the start and length parameters
        cursor.execute("SELECT * FROM track_table LIMIT %s, %s", [start, length])
        rows = cursor.fetchall()
        cursor.execute("SELECT COUNT (*) AS cnt FROM track_table")
        data = cursor.fetchall()
        total_records = data[0][0]

    
    data = [{
        'id' : row[0],
        'status' : row[5],
        'time' : row[3]
    } for row in rows]

    return JsonResponse ({
        'draw':draw,
        'recordsTotal': int(total_records),
        'recordsFiltered' : int(total_records),
        'data':data,
    }, safe=False)