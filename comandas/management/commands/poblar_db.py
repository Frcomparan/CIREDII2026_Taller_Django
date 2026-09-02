from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from comandas.models import Categoria, Mesa, Mesero, Producto


class Command(BaseCommand):
    help = "Crea los catálogos iniciales para el taller"

    @transaction.atomic
    def handle(self, *args, **options):
        meseros = ["Ana", "Carlos", "María"]
        for nombre in meseros:
            Mesero.objects.update_or_create(
                nombre=nombre,
                defaults={"activo": True},
            )

        mesas = {
            1: 2,
            2: 2,
            3: 4,
            4: 4,
            5: 6,
            6: 6,
        }
        for numero, capacidad in mesas.items():
            Mesa.objects.update_or_create(
                numero=numero,
                defaults={"capacidad": capacidad, "activa": True},
            )

        catalogo = {
            "Entradas": [
                ("Guacamole", "85.00"),
                ("Sopa del día", "65.00"),
            ],
            "Platos fuertes": [
                ("Enchiladas", "145.00"),
                ("Hamburguesa", "165.00"),
                ("Tacos de arrachera", "180.00"),
            ],
            "Bebidas": [
                ("Agua natural", "30.00"),
                ("Refresco", "40.00"),
                ("Café", "45.00"),
            ],
            "Postres": [
                ("Flan", "70.00"),
                ("Pastel de chocolate", "85.00"),
            ],
        }

        for nombre_categoria, productos in catalogo.items():
            categoria, _ = Categoria.objects.update_or_create(
                nombre=nombre_categoria,
                defaults={"activa": True},
            )
            for nombre, precio in productos:
                Producto.objects.update_or_create(
                    categoria=categoria,
                    nombre=nombre,
                    defaults={
                        "precio": Decimal(precio),
                        "activo": True,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Base poblada: 3 meseros, 6 mesas, 4 categorías y 10 productos."
            )
        )