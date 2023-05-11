from django.urls import path
from .views import index, user_login, get_data, get_data_by_date, user_logout, user_register, get_users, get_device_by_user, update_decice_by_user

app_name = "app"

urlpatterns = [
    path("", index, name="index"),
    path("login/", user_login, name="login"),
    path("register/", user_register, name="register"),
    path("get-data/", get_data, name='getData'),
    path("get-users/", get_users, name="getUser"),
    path("get-data-by-date/", get_data_by_date, name="getDataByDate"),
    path("get-device-by-user/", get_device_by_user, name="getDeviceByUser"),
    path("update-device-by-user/", update_decice_by_user, name="updateDeviceByUser"),
    path("logout/", user_logout, name="logout")
]
