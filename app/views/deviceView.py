from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from django.http import JsonResponse
from datetime import date, timedelta
from app.models import UserDevice, User
from django.db.models import Q
import json
import math

@login_required
@csrf_exempt
def index(request):
    ids_data = []
    with connections['trackdb'].cursor() as cursor:
        # Get device_id list from track_table so that admin set device according to user email.
        if request.user.is_superuser == 1:
            cursor.execute("SELECT id FROM track_table GROUP BY id")
            ids = cursor.fetchall()
            ids_data = [{"id" : id[0]} for id in ids]
    
    context = {
        'trucks': ids_data
    }

    return render(request, 'index.html', context)

@csrf_exempt
def get_data(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw'), 0)
        start = int(request.POST.get('start'), 0)
        length = int(request.POST.get('length'), 10)
        sort = str(request.POST.get('order[0][dir]'))
        sort_column = str(request.POST.get('order[0][column]'))

        with connections['trackdb'].cursor() as cursor:
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
                    where_clause = " WHERE 1 = 2 "

            # sort column setting.
            sort_col = "a.id"
            if sort_column == "3":
                sort_col = "a.timestamp"
            else:
                sort_col = "b.id"
            
            query =  "  SELECT  a.id, "
            query += "          status, "
            query += "          a.timestamp "
            query += "  FROM    ( "
            query += "              SELECT  id, "
            query += "                      MAX(timestamp) AS timestamp "
            query += "              FROM    track_table "
            query += where_clause
            query += "              GROUP BY id ) A, "
            query += "          track_table B "
            query += "  WHERE   A.id = B.id "
            query += "  AND     A.timestamp = B.timestamp "
            query += "  ORDER BY " + sort_col + " " + sort + " LIMIT %s, %s"
            params = [start, length]
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            query =  "  SELECT  COUNT(*) AS cnt "
            query += "  FROM    ( "
            query += "              SELECT  id, "
            query += "                      MAX(timestamp) AS timestamp "
            query += "              FROM    track_table "
            query += where_clause
            query += "              GROUP BY id ) A "
            cursor.execute(query)
            data = cursor.fetchall()
            total_records = data[0][0]

        data = [{
            'id' : row[0],
            'status' : row[1],
            'time' : row[2]
        } for row in rows]

        return JsonResponse ({
            'draw':draw,
            'recordsTotal': int(total_records),
            'recordsFiltered' : int(total_records),
            'data':data,
        }, safe=False)

@csrf_exempt
def get_map_data(request):
    if request.method == 'POST':
        start_date = float(request.POST['startDate'])
        end_date = float(request.POST['endDate'])
        deviceIds = json.loads(request.POST['ids'])

        with connections['trackdb'].cursor() as cursor:
            query = " SELECT id, lat, lon, timestamp FROM track_table WHERE 1 = 1 "
            if not math.isnan(start_date):
                query +=  " AND timestamp >= " + str(start_date)
            if not math.isnan(end_date):
                query += " AND timestamp <= " + str(end_date)
            if len(deviceIds) > 0:
                query += " AND id IN ('"
                for i, device_id in enumerate(deviceIds):
                    if i > 0:
                        query += "', '"
                    query += str(device_id)
                query += "')"
            print(query)
            cursor.execute(query)
            rows = cursor.fetchall()
            
            data = [{
                'id' : row[0],
                'lat' : row[1],
                'lon' : row[2],
                'timestamp' : row[3]
            } for row in rows]
        return JsonResponse({
            'status' : 'OK',
            'rows' : data
        })



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