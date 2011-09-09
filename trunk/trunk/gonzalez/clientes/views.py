from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from clientes.models import Cliente
# Create your views here.

def lista_clientes(request):
    clientes=Cliente.objects.all()
    return render_to_response("clientes/lista.html",{'clientes':clientes}, RequestContext(request))
