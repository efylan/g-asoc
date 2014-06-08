# coding: latin1
from django import forms
from datetime import date

MONTH = ((1,'Enero'),(2,'Febrero'),(3,'Marzo'),(4,'Abril'),(5,'Mayo'),(6,'Junio'),(7,'Julio'), (8,'Agosto'), (9,'Septiembre'), (10,'Octubre'),(11,'Noviembre'),(12,'Diciembre')) 
YEAR = []
for year in range(2011,2021):
    YEAR.append((year,str(year)))
    
ORDER_CHOICES = ((0,'Orden de captura'),(1,'Por cuenta bancaria'))

class MesForm(forms.Form):
    fecha_inicio = forms.DateField()
    fecha_fin = forms.DateField()
    minimo = forms.DecimalField(max_digits=10, decimal_places=2, label="Minimo para Global", required=False, help_text='No se englobará en caso de estar vacío.')

    def __init__(self, *args, **kwargs):
        super(MesForm, self).__init__(*args, **kwargs)
        hoy = date.today()    
        self.fields['fecha_inicio'].widget.attrs['class'] = 'input_fecha'
        self.fields['fecha_fin'].widget.attrs['class'] = 'input_fecha'

class ContriForm(forms.Form):
    fecha_inicio = forms.DateField()
    fecha_fin = forms.DateField()
    orden = forms.ChoiceField(choices= ORDER_CHOICES, label="Orden")

    def __init__(self, *args, **kwargs):
        super(ContriForm, self).__init__(*args, **kwargs)
        hoy = date.today()    
        self.fields['fecha_inicio'].widget.attrs['class'] = 'input_fecha'
        self.fields['fecha_fin'].widget.attrs['class'] = 'input_fecha'

class FechaForm(forms.Form):
    fecha_inicio = forms.DateField()
    fecha_fin = forms.DateField()

    def __init__(self, *args, **kwargs):
        super(FechaForm, self).__init__(*args, **kwargs)
        hoy = date.today()    
        self.fields['fecha_inicio'].widget.attrs['class'] = 'input_fecha'
        self.fields['fecha_fin'].widget.attrs['class'] = 'input_fecha'
