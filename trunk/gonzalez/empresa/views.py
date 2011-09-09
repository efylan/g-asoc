from django.shortcuts import render_to_response, HttpResponse


def info_empresa(request):
    return render_to_response("empresa/empresa.html",{},)
