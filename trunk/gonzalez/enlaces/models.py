from django.db import models
from django.contrib import admin
# Create your models here.

class Enlace(models.Model):
    nombre = models.CharField(max_length=75)
    website = models.URLField(max_length=75)
    banner = models.ImageField(upload_to="clientes")
    descripcion = models.TextField()

    def __unicode__(self):
        #Hacer seguro para latin1!!!
        return "%s" % self.nombre

class ClienteAdmin(admin.ModelAdmin):
    list_dislplay = ('nombre','giro','website')


try:
    admin.site.register(Cliente, ClienteAdmin)
except:
    pass
