from django.shortcuts import HttpResponseRedirect, render_to_response
from users.forms import LoginForm
from users.models import Perfil
from django.template import RequestContext
from django.contrib import auth
# Create your views here.

def login(request):
    f = LoginForm()
    if request.POST:
        f = LoginForm(request.POST)
        if f.errors:
            return render_to_response('users/login.html', {'form':f}, RequestContext(request))
        else:
            username = f.cleaned_data['username']
            password = f.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    try:
                        request.session['contri'] = user.get_profile().contribuyente
                    except Perfil.DoesNotExist:
                        mensaje = "Usuario sin perfil. Contactar al administrador."
                        return render_to_response('users/login.html', {'form':f, 'mensaje':mensaje}, RequestContext(request))
                    return HttpResponseRedirect('/usuarios/panel/')
                else:
                    mensaje = "Usuario desactivado."
                    return render_to_response('users/login.html', {'form':f, 'mensaje':mensaje}, RequestContext(request))
            else:
                mensaje = "Nombre de usuario o password incorrecto."
                return render_to_response('users/login.html', {'form':f,'mensaje':mensaje}, RequestContext(request))


    else:
        return render_to_response('users/login.html', {'form':f}, RequestContext(request))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
    

def panel(request):
    return render_to_response("users/panel.html", {}, RequestContext(request))
