from django.shortcuts import render_to_response, HttpResponse
from empresa.models import Empresa, Servicio

def info_empresa(request):
    try:
        empresa = Empresa.objects.all()[0]
    except Empresa.DoesNotExist:
        empresa = Empresa()

    return render_to_response("empresa/info.html",{'empresa':empresa},)

def info_servicios(request):
    servicios = Servicio.objects.all().order_by('orden')
    return render_to_response("empresa/servicios.html",{'servicios':servicios},)
