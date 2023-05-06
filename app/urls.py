from django.urls import path
from .views import index, user_login, get_data, get_id_tracks

app_name = "app"

urlpatterns = [
    path("", index, name="index"),
    path("login/", user_login, name="login"),
    path("get-data/", get_data, name='getData'),
    path("get-id-tracks/", get_id_tracks, name="getIdTracks")
]
