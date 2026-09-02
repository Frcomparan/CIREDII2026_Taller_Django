from django.urls import path
from . import views

app_name = "comandas"

urlpatterns = [
  path("", views.tablero_mesas, name="tablero_mesas"),