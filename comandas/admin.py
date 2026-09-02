from django.contrib import admin

from .models import Categoria, Comanda, DetalleComanda, Mesa, Mesero, Producto


admin.site.site_header = "Administración de Comandas Web"
admin.site.site_title = "Comandas Web"
admin.site.index_title = "Catálogos e historial"


@admin.register(Mesero)
class MeseroAdmin(admin.ModelAdmin):
    list_display = ["nombre", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre"]
    list_editable = ["activo"]


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ["numero", "capacidad", "activa", "esta_ocupada"]
    list_filter = ["activa"]
    search_fields = ["=numero"]
    list_editable = ["capacidad", "activa"]

    @admin.display(boolean=True, description="Ocupada")
    def esta_ocupada(self, obj):
        return obj.ocupada


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "activa"]
    list_filter = ["activa"]
    search_fields = ["nombre"]
    list_editable = ["activa"]


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "categoria", "precio", "activo"]
    list_filter = ["activo", "categoria"]
    search_fields = ["nombre", "categoria__nombre"]
    list_editable = ["precio", "activo"]
    list_select_related = ["categoria"]


class DetalleComandaInline(admin.TabularInline):
    model = DetalleComanda
    fields = ["producto", "cantidad", "precio_unitario", "mostrar_subtotal"]
    readonly_fields = fields
    extra = 0
    can_delete = False

    @admin.display(description="Subtotal")
    def mostrar_subtotal(self, obj):
        return obj.subtotal

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Comanda)
class ComandaAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "mesa",
        "mesero",
        "estado",
        "fecha_apertura",
        "fecha_cierre",
        "mostrar_total",
    ]
    list_filter = ["estado", "fecha_apertura", "mesero"]
    search_fields = ["=id", "=mesa__numero", "mesero__nombre"]
    list_select_related = ["mesa", "mesero"]
    readonly_fields = [
        "mesa",
        "mesero",
        "estado",
        "fecha_apertura",
        "fecha_cierre",
        "mostrar_total",
    ]
    inlines = [DetalleComandaInline]

    @admin.display(description="Total")
    def mostrar_total(self, obj):
        return obj.total

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False