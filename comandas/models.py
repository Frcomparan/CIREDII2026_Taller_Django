from django.db import models

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q, Sum
from django.utils import timezone


class Mesero(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "mesero"
        verbose_name_plural = "meseros"

    def __str__(self):
        return self.nombre


class Mesa(models.Model):
    numero = models.PositiveIntegerField(
        unique=True,
        validators=[MinValueValidator(1)],
    )
    capacidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["numero"]
        verbose_name = "mesa"
        verbose_name_plural = "mesas"

    def __str__(self):
        return f"Mesa {self.numero}"

    @property
    def ocupada(self):
        return self.comandas.filter(estado=Comanda.Estado.ABIERTA).exists()

    def clean(self):
        super().clean()
        if self.pk and not self.activa and self.ocupada:
            raise ValidationError(
                {"activa": "No se puede desactivar una mesa con una comanda abierta."}
            )


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
    )
    nombre = models.CharField(max_length=120)
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["categoria__nombre", "nombre"]
        verbose_name = "producto"
        verbose_name_plural = "productos"
        constraints = [
            models.UniqueConstraint(
                fields=["categoria", "nombre"],
                name="producto_unico_por_categoria",
            ),
        ]

    def __str__(self):
        return self.nombre


class Comanda(models.Model):
    class Estado(models.TextChoices):
        ABIERTA = "ABIERTA", "Abierta"
        CERRADA = "CERRADA", "Cerrada"

    mesa = models.ForeignKey(
        Mesa,
        on_delete=models.PROTECT,
        related_name="comandas",
    )
    mesero = models.ForeignKey(
        Mesero,
        on_delete=models.PROTECT,
        related_name="comandas",
    )
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.ABIERTA,
    )
    fecha_apertura = models.DateTimeField(default=timezone.now, editable=False)
    fecha_cierre = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ["-fecha_apertura"]
        verbose_name = "comanda"
        verbose_name_plural = "comandas"
        constraints = [
            models.UniqueConstraint(
                fields=["mesa"],
                condition=Q(estado="ABIERTA"),
                name="una_comanda_abierta_por_mesa",
            ),
            models.CheckConstraint(
                condition=(
                    Q(estado="ABIERTA", fecha_cierre__isnull=True)
                    | Q(
                        estado="CERRADA",
                        fecha_cierre__isnull=False,
                        fecha_cierre__gte=F("fecha_apertura"),
                    )
                ),
                name="comanda_estado_fechas_consistentes",
            ),
        ]

    def __str__(self):
        return f"Comanda {self.pk or 'nueva'} · Mesa {self.mesa.numero}"

    @property
    def total(self):
        resultado = self.detalles.aggregate(
            total=Sum(F("cantidad") * F("precio_unitario"))
        )["total"]
        return resultado or Decimal("0.00")

    def cerrar(self):
        if self.estado == self.Estado.CERRADA:
            return
        if not self.detalles.exists():
            raise ValidationError("No se puede cerrar una comanda sin productos.")
        self.estado = self.Estado.CERRADA
        self.fecha_cierre = timezone.now()
        self.save(update_fields=["estado", "fecha_cierre"])


class DetalleComanda(models.Model):
    comanda = models.ForeignKey(
        Comanda,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="detalles_comanda",
    )
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        editable=False,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "detalle de comanda"
        verbose_name_plural = "detalles de comanda"
        constraints = [
            models.UniqueConstraint(
                fields=["comanda", "producto"],
                name="producto_unico_por_comanda",
            ),
            models.CheckConstraint(
                condition=Q(cantidad__gt=0),
                name="detalle_cantidad_positiva",
            ),
            models.CheckConstraint(
                condition=Q(precio_unitario__gte=0),
                name="detalle_precio_no_negativo",
            ),
        ]

    def __str__(self):
        return f"{self.cantidad} × {self.producto.nombre}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)