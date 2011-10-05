from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from empresa.models import Empresa

def index(request):
    empresa = Empresa.objects.all()[0]
    #empresa = ''
    return render_to_response("index.html", {"empresa":empresa}, RequestContext(request))
