from django import forms

from .models import Mesero, Producto

class SeleccionarMeseroForm(forms.Form):
    mesero = forms.ModelChoiceField(
        queryset=Mesero.objects.none(),
        empty_label=None,
        label="Selecciona tu nombre",
        widget=forms.RadioSelect        
    )

    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)
        self.fields["mesero"].queryset = Mesero.objects.filter(activo=True)

class AgregarProductoForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.none(),
        label="Producto"
    )
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={"min":1})
    )

    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)
        self.fields["producto"].queryset = (
            Producto.objects.filter(
                activo=True,
                categoria__activa=True
            ).select_related("categoria")
            .order_by("categoria__nombre", "nombre")
        )


