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
        cursor.execute("SELECT * FROM track_table LIMIT 0, 20")
        rows = cursor.fetchall()
        cursor.execute("SELECT id FROM track_table GROUP BY id")
        ids = cursor.fetchall()

    # print(rows)
    # print(ids)
    ids_data = [{"id":id[0]} for id in ids]
    data = [{
        'id' : row[0],
        'status' : row[5],
        'time' : row[3],
        'lat' : row[1],
        'lon' : row[2]
    } for row in rows]
    
    context = {
        'rows': data,
        'trucks': ids_data
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
def get_id_tracks(request):
    if request.method == 'POST':
        id = request.POST['id']
        with connections['trackdb'].cursor() as cursor:
            if id == "ALL":
                cursor.execute("SELECT * FROM track_table")
            else:
                cursor.execute("SELECT * FROM track_table WHERE id = %s", [id])
            data = cursor.fetchall()

        return JsonResponse ({
            'status' : 'OK',
            'rows': data,
        })

@csrf_exempt
def get_data(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw'), 0)
        start = int(request.POST.get('start'), 0)
        length = int(request.POST.get('length'), 10)
        sort = str(request.POST.get('order[0][dir]'))
        print(sort)

        with connections['trackdb'].cursor() as cursor:
            # Modify the query to use the start and length parameters
            cursor.execute("SELECT * FROM track_table ORDER BY id " + sort+ " LIMIT %s, %s", [start, length])
            rows = cursor.fetchall()
            cursor.execute("SELECT COUNT (*) AS cnt FROM track_table")
            data = cursor.fetchall()
            total_records = data[0][0]

        
        data = [{
            'id' : row[0],
            'status' : row[5],
            'time' : row[3],
            'lat' : row[1],
            'lon' : row[2]
        } for row in rows]

        return JsonResponse ({
            'draw':draw,
            'recordsTotal': int(total_records),
            'recordsFiltered' : int(total_records),
            'data':data,
        }, safe=False)