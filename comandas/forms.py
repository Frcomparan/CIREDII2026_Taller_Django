from django import forms

from .models import Mesero

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


