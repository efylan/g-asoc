from django.shortcuts import render_to_response, HttpResponseRedirect
from diot.models import Cuenta, Cheque, Proveedor, Concepto
from django.template import RequestContext
from diot.forms import CrearCuentaForm, CrearChequeForm, CrearChequeRapidoForm, AgregarConceptoForm, EditarConceptoForm, EditarChequeRapidoForm
from django.http import Http404

#from django.contrib.auth.decorators import login_required

#@login_required
def cuentas_lista(request):
    contri = request.session['contri']
    cuentas = Cuenta.get_actives.filter(contri__id=contri.id)
    return render_to_response('diot/cuentas/list.html', {'cuentas':cuentas}, RequestContext(request))



def cuentas_crear(request):
    contri = request.session['contri']
    if request.POST:
        f = CrearCuentaForm(request.POST)
        if f.errors:
            return render_to_response('diot/cuentas/create.html', {'form':f}, RequestContext(request))
        else:
            cuenta = f.save(commit=False)
            cuenta.contri=contri
            cuenta.save()
            return HttpResponseRedirect('/diot/cuentas/')
    else:
        f = CrearCuentaForm()
        return render_to_response('diot/cuentas/create.html', {'form':f}, RequestContext(request))

 


def cheques_lista(request):
    contri = request.session['contri']
    cheques = Cheque.get_actives.filter(cuenta__contri__id=contri.id)
    return render_to_response('diot/cheques/list.html', {'cheques':cheques}, RequestContext(request))

def cheques_crear(request):
    contri = request.session['contri']
    if request.POST:
        f = CrearChequeForm(contri,request.POST)
        if f.errors:
            return render_to_response('diot/cheques/create.html', {'form':f}, RequestContext(request))
        else:
            cheque = f.save(commit=False)
            cheque.estado = 1
            cheque.save()
            return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(cheque.fecha.year,cheque.fecha.month))
    else:
        f = CrearChequeForm(contri)
        return render_to_response('diot/cheques/create.html', {'form':f}, RequestContext(request))

def agregar_concepto(request, cheque_id):
    contri = request.session['contri']
    try:
        cheque = Cheque.get_actives.get(id=cheque_id)
    except Cheque.DoesNotExist:
        raise Http404

    if not cheque.cuenta.contri.id == contri.id:
        raise Http404
        
    if request.POST:
        f = AgregarConceptoForm(request.POST)
        if f.errors:
            return render_to_response('diot/cheques/agregar_concepto.html', {'form':f,'cheque':cheque}, RequestContext(request))
        else:
            concepto = f.save(commit=False)

            RFC_proveedor = f.cleaned_data['RFC_proveedor']
            nombre_proveedor = f.cleaned_data['nombre_proveedor']
            impuesto_real = f.cleaned_data['iva_registrado']
            diferencia_iva = f.cleaned_data['diferencia_iva']


            try:
                prov = Proveedor.objects.get(rfc=RFC_proveedor)
            except Proveedor.DoesNotExist:
                prov = Proveedor()
                prov.rfc = RFC_proveedor
                prov.nombre = nombre_proveedor 
                prov.tipo = 1
                prov.activo = True
                prov.save()

            concepto.proveedor=prov
            concepto.cheque=cheque
            concepto.impuesto_real=impuesto_real
            concepto.diferencia_iva = diferencia_iva
            concepto.save()
            return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(cheque.fecha.year,cheque.fecha.month))
    else:
        f = AgregarConceptoForm()
        return render_to_response('diot/cheques/agregar_concepto.html', {'form':f,'cheque':cheque}, RequestContext(request))
    

def cheques_crear_rapido(request):
    contri = request.session['contri']    
    if request.POST:
        f = CrearChequeRapidoForm(contri,request.POST)
        if f.errors:
            return render_to_response('diot/cheques/create.html', {'form':f}, RequestContext(request))
        else:
            cuenta = f.cleaned_data['cuenta']
            referencia = f.cleaned_data['referencia']
            fecha = f.cleaned_data['fecha']
            RFC_proveedor = f.cleaned_data['RFC_proveedor']
            nombre_proveedor = f.cleaned_data['nombre_proveedor']
            beneficiario = f.cleaned_data['beneficiario']
            tipo_concepto = f.cleaned_data['concepto']
            subtotal = f.cleaned_data['subtotal']
            impuesto = f.cleaned_data['impuesto']
            impuesto_real = f.cleaned_data['iva_registrado']
            ret_iva = f.cleaned_data['ret_iva']
            ret_isr = f.cleaned_data['ret_isr']
            importe = f.cleaned_data['importe']
            bancos = f.cleaned_data['bancos']
            diferencia = f.cleaned_data['diferencia']
            diferencia_iva = f.cleaned_data['diferencia_iva']

            cheque = Cheque()
            cheque.referencia = referencia
            cheque.beneficiario = beneficiario
            cheque.cuenta = cuenta
            cheque.importe = importe
            cheque.bancos = bancos
            cheque.fecha = fecha
            cheque.estado = 3 #completo
            cheque.activo = True
            cheque.save()

            try:
                prov = Proveedor.objects.get(rfc=RFC_proveedor)
            except Proveedor.DoesNotExist:
                prov = Proveedor()
                prov.rfc = RFC_proveedor
                prov.nombre = nombre_proveedor 
                prov.tipo = 1
                prov.activo = True
                prov.save()

            concepto = Concepto()
            concepto.cheque = cheque
            concepto.proveedor = prov
            concepto.tipo = tipo_concepto
            concepto.subtotal = subtotal
            concepto.impuesto = impuesto
            concepto.impuesto_real = impuesto_real
            concepto.diferencia_iva = diferencia_iva
            concepto.importe = importe
            concepto.bancos = bancos
            concepto.diferencia = diferencia
            concepto.ret_iva = ret_iva
            concepto.ret_isr = ret_isr

            concepto.activo = True
            concepto.save()


            return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(cheque.fecha.year,cheque.fecha.month))
    else:
        f = CrearChequeRapidoForm(contri)
        return render_to_response('diot/cheques/create.html', {'form':f}, RequestContext(request))


def proveedores_consultar(request):
    if request.POST:
        rfc=request.POST['elegido']
        if not rfc== '':
            try:
                proveedor = Proveedor.objects.get(rfc = rfc)
            except Proveedor.DoesNotExist:
                proveedor={'nombre':''}
            return render_to_response("nombre_proveedor.txt", {'proveedor':proveedor})
    else:
        return render_to_response("nombre_proveedor.txt", {'proveedor':proveedor})


def seleccionar_fecha(request):
    contri = request.session['contri']
    cheques = Cheque.get_actives.filter(cuenta__contri=contri)
    years = cheques.dates('fecha','year')
    archive_list = []
    month_names = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    for year in years: #year is a datetime.datetime object with specific year (month 1 day 1)
        year_dict={}
        year_cheques = cheques.filter(fecha__year=year.year)
        year_dict['entry_count']=year_cheques.count()
        year_dict['date'] = year
        year_dict['value'] = year.year
        months = year_cheques.dates('fecha','month')
        month_list = []
        for month in months: # month is a datetime.datetime object with specified year and month (day 1)
            month_dict={}
            month_cheques = year_cheques.filter(fecha__month=month.month)
            month_dict['entry_count']=month_cheques.count()
            month_dict['date'] = month
            month_dict['value'] = month.month
            month_dict['name'] = month_names[month.month-1]
            days = year_cheques.dates('fecha','day')
            day_list=[]
            for day in days: #Day is a datetime.datetime object with specific year, month and day.
                day_dict={}
                day_cheques = month_cheques.filter(fecha__day=day.day)
                day_dict['entry_count']=day_cheques.count()
                day_dict['date'] = day
                day_dict['value'] = day.day
                day_list.append(day_dict)
            month_dict['days'] = day_list
            month_list.append(month_dict)
        year_dict['months'] = month_list
        archive_list.append(year_dict)
    return render_to_response('diot/cheques/seleccionar_fecha.html',{'archive':archive_list},RequestContext(request))

def cheques_mes(request, year, month):
    contri = request.session['contri']
    cheques = Cheque.get_actives.filter(cuenta__contri__id=contri.id, fecha__year=year,fecha__month=month)
    return render_to_response('diot/cheques/list.html', {'cheques':cheques}, RequestContext(request))



def editar_rapido(request, cheque_id):
    contri = request.session['contri']

    try:
        cheque = Cheque.get_actives.get(id=cheque_id)
    except Cheque.DoesNotExist:
        raise Http404

    if not cheque.cuenta.contri.id == contri.id:
        raise Http404

    f = EditarChequeRapidoForm(contri, cheque)
    if request.POST:
        f = EditarChequeRapidoForm(contri, cheque, request.POST)
        if f.errors:
            return render_to_response('diot/cheques/edit_rapido.html', {'form':f, 'cheque':cheque}, RequestContext(request))
        else:
            cuenta = f.cleaned_data['cuenta']
            referencia = f.cleaned_data['referencia']
            fecha = f.cleaned_data['fecha']
            RFC_proveedor = f.cleaned_data['RFC_proveedor']
            nombre_proveedor = f.cleaned_data['nombre_proveedor']
            beneficiario = f.cleaned_data['beneficiario']
            tipo_concepto = f.cleaned_data['concepto']
            subtotal = f.cleaned_data['subtotal']
            impuesto = f.cleaned_data['impuesto']
            impuesto_real = f.cleaned_data['iva_registrado']
            ret_iva = f.cleaned_data['ret_iva']
            ret_isr = f.cleaned_data['ret_isr']
            importe = f.cleaned_data['importe']
            bancos = f.cleaned_data['bancos']
            diferencia = f.cleaned_data['diferencia']
            diferencia_iva = f.cleaned_data['diferencia_iva']

            cheque.referencia = referencia
            cheque.beneficiario = beneficiario
            cheque.cuenta = cuenta
            cheque.importe = importe
            cheque.bancos = bancos
            cheque.fecha = fecha
            cheque.activo = True
            cheque.save()

            try:
                prov = Proveedor.objects.get(rfc=RFC_proveedor)
            except Proveedor.DoesNotExist:
                prov = Proveedor()
                prov.rfc = RFC_proveedor
                prov.nombre = nombre_proveedor 
                prov.tipo = 1
                prov.activo = True
                prov.save()

            concepto = cheque.concepto_set.all()[0]
            concepto.cheque = cheque
            concepto.proveedor = prov
            concepto.tipo = tipo_concepto
            concepto.subtotal = subtotal
            concepto.impuesto = impuesto
            concepto.impuesto_real = impuesto_real
            concepto.diferencia_iva = diferencia_iva
            concepto.importe = importe
            concepto.bancos = bancos
            concepto.diferencia = diferencia
            concepto.ret_iva = ret_iva
            concepto.ret_isr = ret_isr

            concepto.activo = True
            concepto.save()


            return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(cheque.fecha.year,cheque.fecha.month))
            


    else:
        return render_to_response('diot/cheques/edit_rapido.html', {'form':f, 'cheque':cheque}, RequestContext(request))


def editar_cheque(request, cheque_id):
    contri = request.session['contri']

    try:
        cheque = Cheque.get_actives.get(id=cheque_id)
    except Cheque.DoesNotExist:
        raise Http404

    if not cheque.cuenta.contri.id == contri.id:
        raise Http404

    if request.POST:
        f = CrearChequeForm(contri,request.POST, instance = cheque)
        if f.errors:
            return render_to_response('diot/cheques/edit.html', {'form':f,'cheque':cheque}, RequestContext(request))
        else:
            #cheque = f.save(commit=False)
            cheque.save()
            return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(cheque.fecha.year,cheque.fecha.month))
    else:
        f = CrearChequeForm(contri, instance = cheque)
        return render_to_response('diot/cheques/edit.html', {'form':f,'cheque':cheque}, RequestContext(request))


def editar_concepto(request, concepto_id):
    contri = request.session['contri']
    try:
        concepto = Concepto.objects.get(id=concepto_id)
        cheque = concepto.cheque
    except Cheque.DoesNotExist:
        raise Http404

    if not concepto.cheque.cuenta.contri.id == contri.id:
        raise Http404

    f = EditarConceptoForm(instance = concepto)
    if request.POST:
        f = EditarConceptoForm(request.POST, instance=concepto)
        if f.errors:
            return render_to_response('diot/cheques/editar_concepto.html',{'form':f, 'cheque':cheque, 'ceoncepto':concepto},RequestContext(request))
        else:
            concepto = f.save(commit=False)

            RFC_proveedor = f.cleaned_data['RFC_proveedor']
            nombre_proveedor = f.cleaned_data['nombre_proveedor']
            impuesto_real = f.cleaned_data['iva_registrado']
            diferencia_iva = f.cleaned_data['diferencia_iva']
            try:
                prov = Proveedor.objects.get(rfc=RFC_proveedor)
            except Proveedor.DoesNotExist:
                prov = Proveedor()
                prov.rfc = RFC_proveedor
                prov.nombre = nombre_proveedor 
                prov.tipo = 1
                prov.activo = True
                prov.save()

            concepto.proveedor=prov
            concepto.cheque=cheque
            concepto.impuesto_real=impuesto_real
            concepto.diferencia_iva = diferencia_iva
            concepto.save()


            return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/' % (concepto.cheque.fecha.year, concepto.cheque.fecha.month))

    else:
        return render_to_response('diot/cheques/editar_concepto.html',{'form':f,'cheque':cheque,'concepto':concepto},RequestContext(request))


def eliminar_cheque(request, cheque_id):
    contri = request.session['contri']

    try:
        cheque = Cheque.get_actives.get(id=cheque_id)
        month = cheque.fecha.month
        year = cheque.fecha.year
    except Cheque.DoesNotExist:
        raise Http404

    if not cheque.cuenta.contri.id == contri.id:
        raise Http404

    if request.POST:
        cheque.delete()
        return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(year,month))
    else:
        return render_to_response('diot/cheques/eliminar_cheque.html',{'cheque':cheque}, RequestContext(request))

def eliminar_concepto(request, concepto_id):
    contri = request.session['contri']
    try:
        concepto = Concepto.objects.get(id=concepto_id)
        cheque = concepto.cheque
        month = cheque.fecha.month
        year = cheque.fecha.year
    except Cheque.DoesNotExist:
        raise Http404

    if not cheque.cuenta.contri.id == contri.id:
        raise Http404

    if request.POST:
        concepto.delete()
        return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(year,month))
    else:
        return render_to_response('diot/cheques/eliminar_concepto.html',{'cheque':cheque,'concepto':concepto}, RequestContext(request))

