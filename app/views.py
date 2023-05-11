from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from django.http import JsonResponse
import json
from datetime import date, timedelta
from .forms import UserRegistrationForm, LoginForm
from .models import User, UserDevice
from django.db.models import Q

# Create your views here.

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


@login_required
@csrf_exempt
def index(request):
    ids_data = []
    with connections['trackdb'].cursor() as cursor:

        query = "SELECT * FROM track_table"
        where_clause = ""

        if request.user.is_superuser == 1:
            cursor.execute("SELECT id FROM track_table GROUP BY id")
            ids = cursor.fetchall()
            ids_data = [{"id":id[0]} for id in ids]  
        else:
            user_id = request.user.id
            device_ids = UserDevice.objects.filter(Q(user_id=user_id))
            if device_ids:
                # Build WHERE clause with IN clause for device IDs
                where_clause = " WHERE id IN ('"
                for i, device_id in enumerate(device_ids):
                    if i > 0:
                        where_clause += "', '"
                    where_clause += str(device_id)
                where_clause += "')"
            else:
                where_clause = " WHERE 1 = 2"
            
            query = query + where_clause
        print(query)
        cursor.execute(query)
        rows = cursor.fetchall()

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

@csrf_exempt
def get_data_by_date(request):
    if request.method == 'POST':
        start_date = request.POST['startDate']
        end_date = request.POST['endDate']

        with connections['trackdb'].cursor() as cursor:
            query = "SELECT * FROM track_table WHERE timestamp BETWEEN " + start_date + " AND " + end_date

            if request.user.is_superuser == 0:
                user_id = request.user.id
                device_ids = UserDevice.objects.filter(Q(user_id=user_id))
                if device_ids:
                    # Build WHERE clause with IN clause for device IDs
                    where_clause = " AND id IN ('"
                    for i, device_id in enumerate(device_ids):
                        if i > 0:
                            where_clause += "', '"
                        where_clause += str(device_id)
                    where_clause += "')"
                else:
                    where_clause = " AND 1 = 2"
                
                query = query + where_clause
            
            cursor.execute(query)
            data = cursor.fetchall()
        
        return JsonResponse({
            'status' : 'OK',
            'rows' : data
        })

@csrf_exempt
def get_data(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw'), 0)
        start = int(request.POST.get('start'), 0)
        length = int(request.POST.get('length'), 10)
        sort = str(request.POST.get('order[0][dir]'))
        sort_column = str(request.POST.get('order[0][column]'))

        with connections['trackdb'].cursor() as cursor:
            # Modify the query to use the start and length parameters
            sort_col = "id"
            if sort_column == "1":
                sort_col = 'id'
            elif sort_column == "3":
                sort_col = 'timestamp'
            
            query = "SELECT * FROM track_table "
            where_clause = ""

            if request.user.is_superuser == 0:
                user_id = request.user.id
                device_ids = UserDevice.objects.filter(Q(user_id=user_id))
                if device_ids:
                    # Build WHERE clause with IN clause for device IDs
                    where_clause = " WHERE id IN ('"
                    for i, device_id in enumerate(device_ids):
                        if i > 0:
                            where_clause += "', '"
                        where_clause += str(device_id)
                    where_clause += "')"
                else:
                    where_clause = " WHERE 1 = 2"
                
                query = query + where_clause
            
            query = query + " ORDER BY " + sort_col + " " + sort + " LIMIT %s, %s"
            params = [start, length]

            cursor.execute(query, params)
            rows = cursor.fetchall()

            query = "SELECT COUNT (*) AS cnt FROM track_table"
            if request.user.is_superuser == 0:
                user_id = request.user.id
                device_ids = UserDevice.objects.filter(Q(user_id=user_id))
                if device_ids:
                    # Build WHERE clause with IN clause for device IDs
                    where_clause = " WHERE id IN ('"
                    for i, device_id in enumerate(device_ids):
                        if i > 0:
                            where_clause += "', '"
                        where_clause += str(device_id)
                    where_clause += "')"
                else:
                    where_clause = " WHERE 1 = 2"
                
                query = query + where_clause
            cursor.execute(query)
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

@csrf_exempt
def get_users(request):
    if request.method == 'POST':
        users = User.objects.filter(Q(is_superuser=0) & Q(is_active=1))
    total_records = users.count()
    
    data = [{
        'id': obj.id,
        'email': obj.email,
        'first_name': obj.first_name, 
        'last_name': obj.last_name,
    } for obj in users]
        
    return JsonResponse ({
        'data': data,
        'recordsTotal': int(total_records),
        'recordsFiltered' : int(total_records),
    }, safe=False)

@csrf_exempt
def get_device_by_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        device_ids = UserDevice.objects.filter(Q(user_id=user_id))
    
    data = [{
        'device_id': obj.device_id
    } for obj in device_ids]

    return JsonResponse ({
        'data' : data
    })

@csrf_exempt
def update_decice_by_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        device_ids = request.POST.getlist('device_ids[]')
        
        UserDevice.objects.filter(Q(user_id=user_id)).delete()

        for device in device_ids:
            UserDevice.objects.create(user_id=user_id, device_id=device)

    return JsonResponse({
        'result' : 'success'
    })