from django.db import models
from django.contrib.auth.models import User
from diot.models import Contribuyente
from django.contrib import admin 
# Create your models here.

class Perfil(models.Model):
    user = models.ForeignKey(User, unique=True)
    contribuyente = models.ForeignKey(Contribuyente)
    def __unicode__(self):
        return "%s - %s" % (self.user.username, self.contribuyente)

try:
    admin.site.register(Perfil)
except:
    pass
