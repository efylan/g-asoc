from django import forms
from diot.models import Cuenta, Cheque, Impuesto, Concepto
from diot.models import TIPO_CONCEPTO

MONTH = ((1,'Enero'),(2,'Febrero'),(3,'Marzo'),(4,'Abril'),(5,'Mayo'),(6,'Junio'),(7,'Julio'), (8,'Agosto'), (9,'Septiembre'), (10,'Octubre'),(11,'Noviembre'),(12,'Diciembre')) 
YEAR = ((2011,'2011'), (2012,'2012'))


class CrearCuentaForm(forms.ModelForm):
    class Meta:
        model=Cuenta
        fields = ('numero','banco')

class CrearChequeForm(forms.ModelForm): #Filtrar cuenta en init!
    class Meta:
        model=Cheque
        fields = ('referencia','fecha','beneficiario','cuenta','importe','bancos')

    def __init__(self, contri, *args, **kwargs):
        super(CrearChequeForm, self).__init__(*args, **kwargs)
        self.fields['cuenta'].queryset=Cuenta.get_actives.filter(contri__id=contri.id)



class CrearChequeRapidoForm(forms.Form):
    cuenta = forms.ModelChoiceField(Cuenta.objects.none()) #Filtrar en init!
    referencia = forms.CharField(max_length=20) #Sera que si sera que no?
    fecha = forms.DateTimeField()
    RFC_proveedor = forms.CharField(min_length=12,max_length=18) #hacer txtfield que se actualize con javascript
    nombre_proveedor = forms.CharField(max_length=75) #para crear proveedor
    beneficiario = forms.CharField(max_length=75)
    concepto = forms.ChoiceField(choices = TIPO_CONCEPTO)
    subtotal = forms.DecimalField(max_digits=12, decimal_places=2)
    impuesto = forms.ModelChoiceField(Impuesto.objects, required=False)
    iva = forms.DecimalField(max_digits=12, decimal_places=2, required=False, label='IVA calculado')#X?
    iva_registrado = forms.DecimalField(max_digits=12, decimal_places=2, required=False, label='IVA registrado')#X?
    descuento = forms.DecimalField(max_digits=12, decimal_places=2, initial = 0)
    iva_descuento = forms.DecimalField(max_digits=12, decimal_places=2, initial=0)

    diferencia_iva = forms.DecimalField(max_digits=12, decimal_places=2, required=False, initial=0)#X?
    ret_iva = forms.DecimalField(max_digits=12, decimal_places=2, required=False, initial=0)#?
    ret_isr = forms.DecimalField(max_digits=12, decimal_places=2, required=False, initial=0)#?
    importe = forms.DecimalField(max_digits=12, decimal_places=2) #mismo para concepto?
    bancos = forms.DecimalField(max_digits=12, decimal_places=2)
    diferencia = forms.DecimalField(max_digits=12, decimal_places=2, required=False, initial=0)#X?


    def __init__(self, contri, *args, **kwargs):
        super(CrearChequeRapidoForm, self).__init__(*args, **kwargs)
        self.fields['cuenta'].queryset=Cuenta.get_actives.filter(contri__id=contri.id)
        self.fields['importe'].widget.attrs['readonly']=True
        self.fields['diferencia'].widget.attrs['readonly']=True
        self.fields['diferencia_iva'].widget.attrs['readonly']=True
        self.fields['iva'].widget.attrs['readonly']=True

class AgregarConceptoForm(forms.ModelForm):
    iva = forms.DecimalField(max_digits=12, decimal_places=2, required=False, label='IVA calculado')#X?
    iva_registrado = forms.DecimalField(max_digits=12, decimal_places=2, required=False, label='IVA registrado')#X?
    RFC_proveedor = forms.CharField(min_length=12,max_length=18) #hacer txtfield que se actualize con javascript
    nombre_proveedor = forms.CharField(max_length=75) #para crear proveedor
    bancos = forms.DecimalField(max_digits=12, decimal_places=2)
    diferencia = forms.DecimalField(max_digits=12, decimal_places=2, required=False)#X?
    diferencia_iva = forms.DecimalField(max_digits=12, decimal_places=2, required=False)#X?


    class Meta:
        model = Concepto
        fields = ('RFC_proveedor', 'nombre_proveedor', 'tipo', 'subtotal', 'impuesto', 'iva', 'iva_registrado', 'descuento', 'iva_descuento','diferencia_iva','ret_iva', 'ret_isr', 'importe', 'bancos','diferencia')

    def __init__(self, *args, **kwargs):
        super(AgregarConceptoForm, self).__init__(*args, **kwargs)
        self.fields['importe'].widget.attrs['readonly']=True
        self.fields['diferencia'].widget.attrs['readonly']=True
        self.fields['diferencia_iva'].widget.attrs['readonly']=True
        self.fields['iva'].widget.attrs['readonly']=True



    
class EditarChequeRapidoForm(forms.Form):
    cuenta = forms.ModelChoiceField(Cuenta.objects.none()) #Filtrar en init!
    referencia = forms.CharField(max_length=20) #Sera que si sera que no?
    fecha = forms.DateField()
    RFC_proveedor = forms.CharField(min_length=12,max_length=18) #hacer txtfield que se actualize con javascript
    nombre_proveedor = forms.CharField(max_length=75) #para crear proveedor
    beneficiario = forms.CharField(max_length=75)
    concepto = forms.ChoiceField(choices = TIPO_CONCEPTO)
    subtotal = forms.DecimalField(max_digits=12, decimal_places=2)
    impuesto = forms.ModelChoiceField(Impuesto.objects, required=False)
    iva = forms.DecimalField(max_digits=12, decimal_places=2, required=False, label='IVA calculado')#X?
    iva_registrado = forms.DecimalField(max_digits=12, decimal_places=2, required=False, label='IVA registrado')#X?
    descuento = forms.DecimalField(max_digits=12, decimal_places=2, initial=0)
    iva_descuento = forms.DecimalField(max_digits=12, decimal_places=2, initial=0)
    diferencia_iva = forms.DecimalField(max_digits=12, decimal_places=2, required=False, initial=0)#X?
    ret_iva = forms.DecimalField(max_digits=12, decimal_places=2, required=False, initial=0)#?
    ret_isr = forms.DecimalField(max_digits=12, decimal_places=2, required=False, initial=0)#?
    importe = forms.DecimalField(max_digits=12, decimal_places=2) #mismo para concepto?
    bancos = forms.DecimalField(max_digits=12, decimal_places=2)
    diferencia = forms.DecimalField(max_digits=12, decimal_places=2, required=False, initial=0)#X?


    def __init__(self, contri, cheque, *args, **kwargs):
        super(EditarChequeRapidoForm, self).__init__(*args, **kwargs)
        concepto = cheque.concepto_set.all()[0]
        self.fields['cuenta'].queryset=Cuenta.get_actives.filter(contri__id=contri.id)
        self.fields['importe'].widget.attrs['readonly']=True
        self.fields['diferencia'].widget.attrs['readonly']=True
        self.fields['diferencia_iva'].widget.attrs['readonly']=True
        self.fields['iva'].widget.attrs['readonly']=True
        self.fields['cuenta'].initial = cheque.cuenta
        self.fields['referencia'].initial = cheque.referencia
        self.fields['fecha'].initial = cheque.fecha
        self.fields['RFC_proveedor'].initial = concepto.proveedor.rfc
        self.fields['nombre_proveedor'].initial = concepto.proveedor.nombre
        self.fields['nombre_proveedor'].widget.attrs['readonly']=True
        self.fields['beneficiario'].initial = cheque.beneficiario
        self.fields['concepto'].initial = concepto.tipo
        self.fields['subtotal'].initial = concepto.subtotal
        self.fields['impuesto'].initial = concepto.impuesto
        self.fields['iva'].initial = concepto.get_impuesto_calculado
        self.fields['iva_registrado'].initial = concepto.impuesto_real
        self.fields['diferencia_iva'].initial = concepto.diferencia_iva
        self.fields['ret_iva'].initial = concepto.ret_iva
        self.fields['ret_isr'].initial = concepto.ret_isr
        self.fields['importe'].initial = concepto.importe
        self.fields['bancos'].initial = concepto.bancos
        self.fields['diferencia'].initial = concepto.diferencia



class EditarConceptoForm(forms.ModelForm):
    iva = forms.DecimalField(max_digits=12, decimal_places=2, required=False, label='IVA calculado')#X?
    iva_registrado = forms.DecimalField(max_digits=12, decimal_places=2, required=False, label='IVA registrado')#X?
    RFC_proveedor = forms.CharField(min_length=12,max_length=18) #hacer txtfield que se actualize con javascript
    nombre_proveedor = forms.CharField(max_length=75) #para crear proveedor
    bancos = forms.DecimalField(max_digits=12, decimal_places=2)
    diferencia = forms.DecimalField(max_digits=12, decimal_places=2, required=False)#X?
    diferencia_iva = forms.DecimalField(max_digits=12, decimal_places=2, required=False)#X?


    class Meta:
        model = Concepto
        fields = ('RFC_proveedor', 'nombre_proveedor', 'tipo', 'subtotal', 'impuesto', 'iva', 'iva_registrado', 'descuento', 'iva_descuento','diferencia_iva','ret_iva', 'ret_isr', 'importe', 'bancos','diferencia')

    def __init__(self, *args, **kwargs):
        super(EditarConceptoForm, self).__init__(*args, **kwargs)
        concepto=self.instance

        self.fields['importe'].widget.attrs['readonly']=True
        self.fields['diferencia'].widget.attrs['readonly']=True
        self.fields['diferencia_iva'].widget.attrs['readonly']=True
        self.fields['iva'].widget.attrs['readonly']=True
        self.fields['RFC_proveedor'].initial = concepto.proveedor.rfc
        self.fields['nombre_proveedor'].initial = concepto.proveedor.nombre
        self.fields['nombre_proveedor'].widget.attrs['readonly']=True
        self.fields['tipo'].initial = concepto.tipo
        self.fields['subtotal'].initial = concepto.subtotal
        self.fields['impuesto'].initial = concepto.impuesto
        self.fields['iva'].initial = concepto.get_impuesto_calculado
        self.fields['iva_registrado'].initial = concepto.impuesto_real
        self.fields['diferencia_iva'].initial = concepto.diferencia_iva
        self.fields['ret_iva'].initial = concepto.ret_iva
        self.fields['ret_isr'].initial = concepto.ret_isr
        self.fields['importe'].initial = concepto.importe
        self.fields['bancos'].initial = concepto.bancos
        self.fields['diferencia'].initial = concepto.diferencia


class CrearTotalForm(forms.Form):
    cuenta = forms.ModelChoiceField(Cuenta.objects.none())
    total = forms.DecimalField(max_digits=12, decimal_places=2)
    month = forms.ChoiceField(choices = MONTH)
    year = forms.ChoiceField(choices = YEAR)

    def __init__(self, month, year, contri, *args, **kwargs):
        super(CrearTotalForm, self).__init__(*args, **kwargs)
        self.fields['month'].initial = month
        self.fields['year'].initial = year
        self.fields['cuenta'].queryset=Cuenta.get_actives.filter(contri__id=contri.id)

class EditarTotalForm(forms.Form):
    cuenta = forms.ModelChoiceField(Cuenta.objects.none())
    total = forms.DecimalField(max_digits=12, decimal_places=2)
    month = forms.ChoiceField(choices = MONTH)
    year = forms.ChoiceField(choices = YEAR)

    def __init__(self, tmensual, *args, **kwargs):
        super(EditarTotalForm, self).__init__(*args, **kwargs)
        self.fields['month'].initial = tmensual.month
        self.fields['year'].initial = tmensual.year
        self.fields['total'].initial = tmensual.total
        self.fields['cuenta'].queryset=Cuenta.get_actives.filter(contri__id=tmensual.contri.id)
        self.fields['cuenta'].initial = tmensual.cuenta

