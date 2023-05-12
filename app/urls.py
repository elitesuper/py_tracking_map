from django.urls import path
from app.views.userView import user_login, user_logout, user_register
from app.views.deviceView import index, get_data, get_map_data, get_users, get_device_by_user, update_decice_by_user
app_name = "app"

urlpatterns = [
    path("", index, name="index"),
    path("login/", user_login, name="login"),
    path("register/", user_register, name="register"),
    path("get-data/", get_data, name='getData'),
    path("get-users/", get_users, name="getUser"),
    path("get-map-data/", get_map_data, name="getMapData"),
    path("get-device-by-user/", get_device_by_user, name="getDeviceByUser"),
    path("update-device-by-user/", update_decice_by_user, name="updateDeviceByUser"),
    path("logout/", user_logout, name="logout")
]
