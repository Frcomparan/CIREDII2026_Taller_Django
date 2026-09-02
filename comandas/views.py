from django.contrib import messages
from django.db.models import Exists, OuterRef, Q, Subquery
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import SeleccionarMeseroForm

from .models import Comanda, Mesa, Mesero

CLAVE_MESERO_SESION = "mesero_activo_id"

def seleccionar_mesero(request):
  if request.method == "POST":
    form = SeleccionarMeseroForm(request.POST)
    if form.is_valid():
      mesero = form.cleaned_data["mesero"]
      request.session[CLAVE_MESERO_SESION] = mesero.id
      messages.success(request, f"Mesero {mesero.nombre} seleccionado.")
      return redirect("comandas:tablero_mesas")

  else:
    form = SeleccionarMeseroForm()
    render(
      request,
      "comandas/seleccionar_mesero.html",
      {"form": form}
    )

@require_POST
def cambiar_mesero(request):
  request.session.pop(CLAVE_MESERO_SESION, None)
  messages.info(request, "Selecciona al mesero que continuará operando")
  return redirect("comandas:seleccionar_mesero")

def tablero_mesas(request):
  mesero_id = request.session.get(CLAVE_MESERO_SESION)
  if mesero_id is None:
    messages.info(request, "Selecciona un mesero para continuar")
    return redirect("comandas:seleccionar_mesero")

  try:
    mesero_activo = Mesero.objects.get(pk=mesero_id, activo=True)
  except Mesero.DoesNotExist:
    messages.warning(request, "El mesero seleccionado no existe o no está activo.")
    return redirect("comandas:seleccionar_mesero")

  comandas_abiertas = Comanda.objects.filter(
    mesa=OuterRef('pk'),
    estado=Comanda.Estado.ABIERTA
  )

  mesas = Mesa.objects.annotate(
    tiene_comanda_abierta=Exists(comandas_abiertas),
    comanda_abierta_id=Subquery(
      comandas_abiertas.values('id')[:1]
      ),
  ).filter(Q(tiene_comanda_abierta=True) | Q(activo=True)).order_by('numero')

  return render(
    request,
    "comandas/tablero_mesas.html",
    {
      "mesero_activo": mesero_activo,
      "mesas": mesas,
    }
  )