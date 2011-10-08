from django import forms
from diot.models import Contribuyente

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class SeleccionarContriForm(forms.Form):
    contri = forms.ModelChoiceField(Contribuyente.objects.all(), label="Contribuyente", help_text="Seleccione un contribuyente para usar el sistema. Lo puede cambiar en cualquier momento dando click en su nombre de usuario en la seccion superior.")
