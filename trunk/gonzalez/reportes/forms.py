# coding: latin1
from django import forms
from datetime import date

MONTH = ((1,'Enero'),(2,'Febrero'),(3,'Marzo'),(4,'Abril'),(5,'Mayo'),(6,'Junio'),(7,'Julio'), (8,'Agosto'), (9,'Septiembre'), (10,'Octubre'),(11,'Noviembre'),(12,'Diciembre')) 
YEAR = ((2011,'2011'), (2012,'2012'))
ORDER_CHOICES = ((0,'Orden de captura'),(1,'Por cuenta bancaria'))

class MesForm(forms.Form):
    month = forms.ChoiceField(choices = MONTH, label="Mes")
    year = forms.ChoiceField(choices = YEAR, label="Año")
    minimo = forms.DecimalField(max_digits=10, decimal_places=2, label="Minimo para Global", required=False, help_text='No se englobará en caso de estar vacío.')

    def __init__(self, *args, **kwargs):
        super(MesForm, self).__init__(*args, **kwargs)
        hoy = date.today()    
        self.fields['month'].initial = hoy.month
        self.fields['year'].initial = hoy.year

class ContriForm(forms.Form):
    month = forms.ChoiceField(choices = MONTH, label="Mes")
    year = forms.ChoiceField(choices = YEAR, label="Año")
    orden = forms.ChoiceField(choices= ORDER_CHOICES, label="Orden")

    def __init__(self, *args, **kwargs):
        super(ContriForm, self).__init__(*args, **kwargs)
        hoy = date.today()    
        self.fields['month'].initial = hoy.month
        self.fields['year'].initial = hoy.year

class FechaForm(forms.Form):
    month = forms.ChoiceField(choices = MONTH, label="Mes")
    year = forms.ChoiceField(choices = YEAR, label="Año")

    def __init__(self, *args, **kwargs):
        super(FechaForm, self).__init__(*args, **kwargs)
        hoy = date.today()    
        self.fields['month'].initial = hoy.month
        self.fields['year'].initial = hoy.year
