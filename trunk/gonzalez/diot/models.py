from django.db import models
from django.contrib import admin


TIPO_CONCEPTO = ((1,"Compras"),(2,"Gastos"),(3,"Honorarios"),(4,"Renta"),(5,"Pago de Impuestos"),(6,"Movimientos Bancarios"),(7, "Activos Fijos"),(8,"Otros"))
TIPO_PROVEEDOR = ((1,"Nacional"),(2,"Extranjero"),(1,"Global"))
ESTADO_CHEQUE = ((1,"Nuevo"),(2,"Pendiente"),(3,"Completo"),(4,"Borrado"))

#------------------------------------------------------------

class Contribuyente(models.Model):
    nombre = models.CharField(max_length=75)
    rfc = models.CharField(max_length=14, unique=True)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s - %s" % (self.nombre, self.rfc)

try:
    admin.site.register(Contribuyente)
except:
    pass
    

#------------------------------------------------------------

class Proveedor(models.Model):
    rfc = models.CharField(max_length=14, unique=True)
    nombre = models.CharField(max_length=75) 
    tipo = models.PositiveSmallIntegerField(choices=TIPO_PROVEEDOR, null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s - %s - %s" % (self.nombre, self.rfc, self.get_tipo_display())

try:
    admin.site.register(Proveedor)
except:
    pass

#------------------------------------------------------------

class Banco(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % (self.nombre)

try:
    admin.site.register(Banco)
except:
    pass

#------------------------------------------------------------

class ActiveCuentaManager(models.Manager):
    def get_query_set(self):
        return super(ActiveCuentaManager, self).get_query_set().filter(activo=1)

class CuentaManager(models.Manager):
    def get_query_set(self):
        return super(CuentaManager, self).get_query_set()


class Cuenta(models.Model):
    numero = models.CharField(max_length=25,unique=True)
    banco = models.ForeignKey(Banco)
    contri = models.ForeignKey(Contribuyente)
    activo = models.BooleanField(default=True)
    objects = CuentaManager()
    get_actives = ActiveCuentaManager()

    def __unicode__(self):
        return "%s - %s" % (self.banco.nombre, self.numero)
try:
    admin.site.register(Cuenta)
except:
    pass

#------------------------------------------------------------

class Impuesto(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s - %s" % (self.nombre, self.porcentaje)

try:
    admin.site.register(Impuesto)
except:
    pass

#------------------------------------------------------------
class ActiveChequeManager(models.Manager):
    def get_query_set(self):
        return super(ActiveChequeManager, self).get_query_set().filter(activo=1)

class ChequeManager(models.Manager):
    def get_query_set(self):
        return super(ChequeManager, self).get_query_set()


class Cheque(models.Model):
    referencia = models.CharField(max_length=20) #Sera que si sera que no?
    beneficiario = models.CharField(max_length=75)
    cuenta = models.ForeignKey(Cuenta)
    importe = models.DecimalField(max_digits=12, decimal_places=2) #ELIMINAR?
    bancos = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    estado = models.PositiveSmallIntegerField(choices=ESTADO_CHEQUE)
    activo = models.BooleanField(default=True)
    objects = ChequeManager()
    get_actives = ActiveChequeManager()
    def __unicode__(self):
        return "%s - %s - %s" % (self.referencia, self.cuenta, self.beneficiario)

    def get_diferencia(self):
        conceptos = self.concepto_set.all()
        total = 0
        for concepto in conceptos:
            total+=concepto.bancos
        diferencia = self.bancos - total
        return diferencia


#------------------------------------------------------------
    
class Concepto(models.Model):
    cheque = models.ForeignKey(Cheque)
    proveedor = models.ForeignKey(Proveedor)
    tipo = models.PositiveSmallIntegerField(choices = TIPO_CONCEPTO)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    impuesto = models.ForeignKey(Impuesto, blank=True, null=True)
    impuesto_real = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='IVA registrado')
    diferencia_iva = models.DecimalField(max_digits=12, decimal_places=2)
    importe = models.DecimalField(max_digits=12, decimal_places=2)
    bancos = models.DecimalField(max_digits=12, decimal_places=2)
    diferencia = models.DecimalField(max_digits=12, decimal_places=2)
    ret_iva = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ret_isr = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s - %s - %s" % (self.fecha, self.proveedor, self.tipo)

    def get_impuesto_calculado(self):
        if self.impuesto == None:
            impuesto=0
        else:
            impuesto = (self.subtotal) * (self.impuesto.porcentaje/100)
        return impuesto

    def get_importe_calculado(self):
        importe = self.subtotal + self.get_impuesto_calculado()
        return importe

    def get_diferencia_iva(self):
        calc = self.get_impuesto_calculado()
        real = self.impuesto_real
        diff = real - calc        
        return diff

    def get_diferencia_importe(self):
        calc = self.get_importe_calculado()
        real = self.bancos
        diff = real - calc        
        return diff

    def tiene_diferencia_importe(self):
        if self.get_diferencia_importe <> 0:
            return True

    def tiene_diferencia_iva(self):
        if self.get_diferencia_impuesto <> 0:
            return True

#------------------------------------------------------------

