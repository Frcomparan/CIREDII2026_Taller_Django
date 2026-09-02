from django.urls import path
from . import views

app_name = "comandas"

urlpatterns = [
    path("", views.tablero_mesas, name="inicio"),
    path("mesas/", views.tablero_mesas, name="tablero_mesas"),
        path(
        "mesas/<int:mesa_id>/abrir/",
        views.abrir_comanda,
        name="abrir_comanda",
    ),
    path(
      "meseros/seleccionar/",
      views.seleccionar_mesero,
      name="seleccionar_mesero"
    ),
    path(
      "meseros/cambiar/",
      views.cambiar_mesero,
      name="cambiar_mesero"
    ),
    path(
      "comandas/<int:pk>",
      views.detalle_comanda,
      name="detalle_comanda"
      ),
    path(
      "comandas/<int:pk>/productos/agregar/",
      views.agregar_producto,
      name="agregar_producto"
      )
]


