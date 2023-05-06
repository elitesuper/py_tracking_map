from django.urls import path
from .views import index, user_login

app_name = "app"

urlpatterns = [
    path("", index, name="index"),
    path("login/", user_login, name="login"),
]
