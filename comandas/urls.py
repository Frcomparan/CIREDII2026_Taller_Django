from django.urls import path
from . import views

app_name = "comandas"

urlpatterns = [
    path("", views.tablero_mesas, name="inicio"),
    path("mesas/", views.tablero_mesas, name="tablero_mesas"),
    path(
      "meseros/seleccionar/",
      views.seleccionar_mesero,
      name="seleccionar_mesero"
    ),
    path(
      "meseros/cambiar/",
      views.cambiar_mesero,
      name="cambiar_mesero"
    )
]


