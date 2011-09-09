from django.db import models
from django.contrib import admin
from PIL import Image

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=75)
    giro = models.CharField(max_length=30)
    website = models.URLField(max_length=75)
    banner = models.ImageField(upload_to="clientes")
    descripcion = models.TextField()

    def __unicode__(self):
        #Hacer seguro para latin1!!!
        return "%s" % self.nombre

    def save(self):
        super(Cliente, self).save()
        if self.banner:
            self.resize_img(self.banner)

    def resize_img(self, imagen):
        maxw=200
        maxh=200
        method= Image.ANTIALIAS
        w=imagen.width
        h=imagen.height
        print w, h
        path=imagen.path
        if h<=maxh and w<=maxw:
            pass
        else:
            pict= Image.open(path)
            imAspect=float(w)/float(h)
            outAspect=float(maxw)/float(maxh)

            if imAspect>=outAspect:
                img=pict.resize((maxw, int((float(maxw)/imAspect)+0.5)), method)
                img.save(path)
            else:
                img=pict.resize((int((float(maxh)*imAspect)+0.5),maxh),method)
                img.save(path)


class ClienteAdmin(admin.ModelAdmin):
    list_dislplay = ('nombre','giro','website')


try:
    admin.site.register(Cliente, ClienteAdmin)
except:
    pass
