from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Exists, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    AgregarProductoForm,
    SeleccionarMeseroForm,
)

from .models import Comanda, DetalleComanda, Mesa, Mesero

CLAVE_MESERO_SESION = "mesero_activo_id"

def obtener_mesero_activo(request):
    mesero_id = request.session.get(CLAVE_MESERO_SESION)
    if mesero_id is None:
        return None

    try:
        return Mesero.objects.get(pk=mesero_id, activo=True)
    except Mesero.DoesNotExist:
        request.session.pop(CLAVE_MESERO_SESION, None)
        return None

def seleccionar_mesero(request):
  if request.method == "POST":
    form = SeleccionarMeseroForm(request.POST)
    if form.is_valid():
      mesero = form.cleaned_data["mesero"]
      request.session[CLAVE_MESERO_SESION] = mesero.pk
      messages.success(request, f"Mesero {mesero.nombre} seleccionado.")
      return redirect("comandas:tablero_mesas")

  else:
    form = SeleccionarMeseroForm()

    return render(
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
  ).filter(Q(tiene_comanda_abierta=True) | Q(activa=True)).order_by('numero')

  return render(
    request,
    "comandas/tablero_mesas.html",
    {
      "mesero_activo": mesero_activo,
      "mesas": mesas,
    }
  )


@require_POST
def abrir_comanda(request, mesa_id):
    mesero_activo = obtener_mesero_activo(request)
    if mesero_activo is None:
        messages.info(request, "Selecciona un mesero para continuar.")
        return redirect("comandas:seleccionar_mesero")

    try:
        with transaction.atomic():
            mesa = Mesa.objects.select_for_update().get(
                pk=mesa_id,
                activa=True,
            )

            comanda = Comanda.objects.filter(
                mesa=mesa,
                estado=Comanda.Estado.ABIERTA,
            ).first()

            if comanda is None:
                comanda = Comanda.objects.create(
                    mesa=mesa,
                    mesero=mesero_activo,
                )
                messages.success(
                    request,
                    f"Se abrió la comanda de la mesa {mesa.numero}.",
                )
            else:
                messages.info(request, "La mesa ya tenía una comanda abierta.")
    except Mesa.DoesNotExist:
        messages.error(request, "La mesa no existe o está inactiva.")
        return redirect("comandas:tablero_mesas")
    except IntegrityError:
        comanda = Comanda.objects.filter(
            mesa_id=mesa_id,
            estado=Comanda.Estado.ABIERTA,
        ).first()
        if comanda is None:
            messages.error(request, "No fue posible abrir la comanda.")
            return redirect("comandas:tablero_mesas")
        messages.info(request, "Otra solicitud abrió primero la comanda.")

    return redirect("comandas:detalle_comanda", pk=comanda.pk)

def detalle_comanda(request, pk):
    mesero_activo = obtener_mesero_activo(request)
    if mesero_activo is None:
        messages.info(request, "Selecciona un mesero para continuar.")
        return redirect("comandas:seleccionar_mesero")

    comanda = get_object_or_404(
        Comanda.objects.select_related("mesa", "mesero").prefetch_related(
            "detalles__producto__categoria"
        ),
        pk=pk,
    )

    if comanda.estado != Comanda.Estado.ABIERTA:
        messages.info(request, "La comanda ya está cerrada.")
        return redirect("comandas:ver_ticket", pk=comanda.pk)

    return render(
        request,
        "comandas/detalle_comanda.html",
        {
            "mesero_activo": mesero_activo,
            "comanda": comanda,
            "form": AgregarProductoForm(),
        },
    )


@require_POST
def agregar_producto(request, pk):
    mesero_activo = obtener_mesero_activo(request)
    if mesero_activo is None:
        messages.info(request, "Selecciona un mesero para continuar.")
        return redirect("comandas:seleccionar_mesero")

    comanda = get_object_or_404(
        Comanda.objects.select_related("mesa", "mesero"),
        pk=pk,
    )
    form = AgregarProductoForm(request.POST)

    if not form.is_valid():
        comanda = Comanda.objects.select_related(
            "mesa", "mesero"
        ).prefetch_related("detalles__producto__categoria").get(pk=pk)
        return render(
            request,
            "comandas/detalle_comanda.html",
            {
                "mesero_activo": mesero_activo,
                "comanda": comanda,
                "form": form,
            },
            status=400,
        )

    producto = form.cleaned_data["producto"]
    cantidad = form.cleaned_data["cantidad"]

    with transaction.atomic():
        comanda = get_object_or_404(
            Comanda.objects.select_for_update(),
            pk=pk,
        )

        if comanda.estado != Comanda.Estado.ABIERTA:
            messages.warning(request, "La comanda ya no admite cambios.")
            return redirect("comandas:tablero_mesas")

        detalle, creado = DetalleComanda.objects.get_or_create(
            comanda=comanda,
            producto=producto,
            defaults={"cantidad": cantidad},
        )

        if not creado:
            detalle.cantidad += cantidad
            detalle.save(update_fields=["cantidad"])

    if creado:
        messages.success(request, f"Se agregó {producto.nombre}.")
    else:
        messages.success(request, f"Se actualizó {producto.nombre}.")

    return redirect("comandas:detalle_comanda", pk=comanda.pk)
