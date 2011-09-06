from django.db import models
from django.contrib import admin

class Empresa(models.Model):
    nombre = models.CharField(max_length=70)
    ciudad = models.CharField(max_length=30)
    estado = models.CharField(max_length=30)
    pais = models.CharField(max_length=30)
    direccion = models.TextField()
    razon_social = models.TextField()
    mision = models.TextField()
    vision = models.TextField()
    telefono = models.CharField(max_length=20)
    fax = models.CharField(max_length=20)
    email = models.EmailField(verbose_name="Correo Electronico")
    rfc = models.CharField(max_length=14, verbose_name="RFC")

    def __unicode__(self):
        return "%s (%s)" % (self.nombre, self.rfc)

class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre','ciudad','estado','pais','direccion','telefono','fax','email','rfc')

try:
    admin.site.register(Empresa,EmpresaAdmin)
except:
    pass
