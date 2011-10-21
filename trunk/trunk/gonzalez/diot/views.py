from django.shortcuts import render_to_response, HttpResponseRedirect
from diot.models import Cuenta, Cheque, Proveedor, Concepto, COMPRAS, GASTOS, HONORARIOS, RENTA, IMPUESTOS, MOV_BANCARIOS, ACT_FIJO, OTROS, SUELDOS

from django.template import RequestContext
from diot.forms import CrearCuentaForm, CrearChequeForm, CrearChequeRapidoForm, AgregarConceptoForm, EditarConceptoForm, EditarChequeRapidoForm, CrearTotalForm, EditarTotalForm
from django.http import Http404
from diot.models import TotalMensual
#from django.contrib.auth.decorators import login_required
#TODO escribir una adivinada de operacion de proveedor por el concepto que se metio primero


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
            if 'add_concepto' in request.POST:
                return HttpResponseRedirect('/diot/cheques/%s/agregar_concepto/' % cheque.id)
            else:
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
            if 'add_concepto' in request.POST:
                return HttpResponseRedirect('/diot/cheques/%s/agregar_concepto/' % cheque.id)
            else:
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
            descuento = f.cleaned_data['descuento']
            iva_descuento = f.cleaned_data['iva_descuento']
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
            concepto.descuento = descuento
            concepto.iva_descuento = iva_descuento
            concepto.diferencia_iva = diferencia_iva
            concepto.importe = importe
            concepto.bancos = bancos
            concepto.diferencia = diferencia
            concepto.ret_iva = ret_iva
            concepto.ret_isr = ret_isr

            concepto.activo = True
            concepto.save()

            if 'add_concepto' in request.POST:
                return HttpResponseRedirect('/diot/cheques/crear_rapido/')
            else:
                return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(cheque.fecha.year,cheque.fecha.month))

    else:
        f = CrearChequeRapidoForm(contri)
        return render_to_response('diot/cheques/cheques_rapido.html', {'form':f}, RequestContext(request))


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
    final = get_all_totales(cheques)
    resumen = resumen_cuentas(cheques, contri)
    mensuales = TotalMensual.objects.filter(contri=contri, month=month, year=year)

    return render_to_response('diot/cheques/list.html', {'cheques':cheques,'final':final, 'resumen':resumen, 'mensuales':mensuales,'month':month, 'year':year}, RequestContext(request))



def editar_rapido(request, cheque_id):
    contri = request.session['contri']

    try:
        cheque = Cheque.get_actives.get(id=cheque_id)
        concepto = cheque.concepto_set.all()[0]
    except Cheque.DoesNotExist:
        raise Http404

    if not cheque.cuenta.contri.id == contri.id:
        raise Http404

    f = EditarChequeRapidoForm(contri, cheque)
    if request.POST:
        f = EditarChequeRapidoForm(contri, cheque, request.POST)
        if f.errors:
            return render_to_response('diot/cheques/edit_rapido.html', {'form':f, 'cheque':cheque, 'concepto':concepto}, RequestContext(request))
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
            descuento = f.cleaned_data['descuento']
            iva_descuento = f.cleaned_data['iva_descuento']

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
            concepto.descuento = descuento
            concepto.iva_descuento = iva_descuento
            concepto.diferencia_iva = diferencia_iva
            concepto.importe = importe
            concepto.bancos = bancos
            concepto.diferencia = diferencia
            concepto.ret_iva = ret_iva
            concepto.ret_isr = ret_isr

            concepto.activo = True
            concepto.save()


            if 'add_concepto' in request.POST:
                return HttpResponseRedirect('/diot/cheques/crear_rapido/')
            elif 'add_anterior' in request.POST:
                return HttpResponseRedirect('/diot/conceptos/anterior/%s/' % concepto.id)
            elif 'add_siguiente' in request.POST:
                return HttpResponseRedirect('/diot/conceptos/siguiente/%s/' % concepto.id)
            else:
                return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(cheque.fecha.year,cheque.fecha.month))




    else:
        return render_to_response('diot/cheques/edit_rapido.html', {'form':f, 'cheque':cheque, 'concepto':concepto}, RequestContext(request))


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

            if 'add_concepto' in request.POST:
                return HttpResponseRedirect('/diot/cheques/%s/agregar_concepto/' % cheque.id)
            elif 'add_anterior' in request.POST:
                return HttpResponseRedirect('/diot/conceptos/anterior/%s/' % concepto.id)
            elif 'add_siguiente' in request.POST:
                return HttpResponseRedirect('/diot/conceptos/siguiente/%s/' % concepto.id)
            else:
                return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(cheque.fecha.year,cheque.fecha.month))

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



def get_totales(cheques):
    dict_totales={}
    dict_totales['base_0'] = 0
    dict_totales['sub_11'] = 0
    dict_totales['sub_16'] = 0
    dict_totales['iva_11'] = 0
    dict_totales['iva_16'] = 0
    dict_totales['ret_iva'] = 0
    dict_totales['ret_isr'] = 0
    dict_totales['importe'] = 0
    dict_totales['bancos'] = 0
    dict_totales['diff'] = 0
    dict_totales['diff_11'] = 0
    dict_totales['diff_16'] = 0
    for cheque in cheques:
        for concepto in cheque.concepto_set.all():
            if concepto.impuesto==None:
                dict_totales['base_0'] += concepto.subtotal
            elif concepto.impuesto.porcentaje==11:
                dict_totales['sub_11'] += concepto.subtotal
                dict_totales['iva_11'] += concepto.impuesto_real
                dict_totales['diff_11'] += concepto.diferencia_iva
            elif concepto.impuesto.porcentaje ==16:
                dict_totales['sub_16'] += concepto.subtotal
                dict_totales['iva_16'] += concepto.impuesto_real
                dict_totales['diff_16'] += concepto.diferencia_iva

            dict_totales['ret_iva'] += concepto.ret_iva
            dict_totales['ret_isr'] += concepto.ret_isr
            dict_totales['importe'] += concepto.importe
            dict_totales['bancos'] += concepto.bancos
            dict_totales['diff']   += concepto.diferencia

    dict_totales['total_acredible'] = dict_totales['iva_11'] + dict_totales['iva_16']
    dict_totales['ded_autorizadas'] = dict_totales['base_0'] + dict_totales['sub_11'] + dict_totales['sub_16']
    return dict_totales


def totales_tipos(conceptos):
    tipos = [COMPRAS, GASTOS, HONORARIOS, RENTA, IMPUESTOS, MOV_BANCARIOS, ACT_FIJO, OTROS]
    totales_list=[]
    for tipo in tipos:
        totales_tipo={}
        totales_tipo['nombre'] = get_tipo_nombre(tipo)
        totales_tipo['base_0'] = 0
        totales_tipo['sub_11'] = 0
        totales_tipo['sub_16'] = 0
        conceptos_tipo = conceptos.filter(tipo=tipo)
        print tipo
        for concepto in conceptos_tipo:
            if concepto.impuesto == None:
                totales_tipo['base_0']+=concepto.subtotal
            elif concepto.impuesto.porcentaje == 11:
                totales_tipo['sub_11']+=concepto.subtotal
            elif concepto.impuesto.porcentaje == 16:
                totales_tipo['sub_16']+=concepto.subtotal
        print totales_tipo
        totales_tipo['subtotal'] = totales_tipo['base_0'] + totales_tipo['sub_11'] + totales_tipo['sub_16']

        totales_list.append(totales_tipo)

    return totales_list


def get_tipo_nombre(tipo):
    if tipo == COMPRAS:
        return "COMPRAS"
    elif tipo == GASTOS:
        return "GASTOS"
    elif tipo == HONORARIOS:
        return "HONORARIOS"
    elif tipo == RENTA:
        return "RENTA"
    elif tipo == IMPUESTOS:
        return "PAGO DE IMPUESTOS"
    elif tipo == MOV_BANCARIOS:
        return "MOVIMIENTOS BANCARIOS"
    elif tipo == ACT_FIJO:
        return "ACTIVO FIJO"
    elif tipo == OTROS:
        return "OTROS"
    else:
        return "NONE"


def get_all_totales(cheques):
    dict_totales={}
    dict_totales['base_0'] = 0
    dict_totales['sub_11'] = 0
    dict_totales['sub_16'] = 0
    dict_totales['iva_11'] = 0
    dict_totales['iva_16'] = 0
    dict_totales['ret_iva'] = 0
    dict_totales['ret_isr'] = 0
    dict_totales['importe'] = 0
    dict_totales['bancos'] = 0
    dict_totales['diff'] = 0
    dict_totales['diff_11'] = 0
    dict_totales['diff_16'] = 0
    dict_tipos={}
    dict_tipos['compras'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0}
    dict_tipos['gastos'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0}
    dict_tipos['honorarios'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0}
    dict_tipos['renta'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0}
    dict_tipos['impuestos'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0}
    dict_tipos['mov_bancarios'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0}
    dict_tipos['act_fijo'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0}
    dict_tipos['otros'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0}
    dict_tipos['sueldos'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0}

    for cheque in cheques:
        for concepto in cheque.concepto_set.all():
            if concepto.impuesto==None:
                dict_totales['base_0'] += concepto.subtotal
                if concepto.tipo == COMPRAS:
                    dict_tipos['compras']['base_0']+=concepto.subtotal
                elif concepto.tipo == GASTOS:
                    dict_tipos['gastos']['base_0']+=concepto.subtotal
                elif concepto.tipo == HONORARIOS:
                    dict_tipos['honorarios']['base_0']+=concepto.subtotal
                elif concepto.tipo == RENTA:
                    dict_tipos['renta']['base_0']+=concepto.subtotal
                elif concepto.tipo == IMPUESTOS:
                    dict_tipos['impuestos']['base_0']+=concepto.subtotal
                elif concepto.tipo == MOV_BANCARIOS:
                    dict_tipos['mov_bancarios']['base_0']+=concepto.subtotal
                elif concepto.tipo == ACT_FIJO:
                    dict_tipos['act_fijo']['base_0']+=concepto.subtotal
                elif concepto.tipo == OTROS:
                    dict_tipos['otros']['base_0']+=concepto.subtotal
                elif concepto.tipo == SUELDOS:
                    dict_tipos['sueldos']['base_0']+=concepto.subtotal



            elif concepto.impuesto.porcentaje==11:
                dict_totales['sub_11'] += concepto.subtotal
                dict_totales['iva_11'] += concepto.impuesto_real
                dict_totales['diff_11'] += concepto.diferencia_iva


                if concepto.tipo == COMPRAS:
                    dict_tipos['compras']['sub_11']+=concepto.subtotal
                    dict_tipos['compras']['iva_11']+=concepto.impuesto_real
                elif concepto.tipo == GASTOS:
                    dict_tipos['gastos']['sub_11']+=concepto.subtotal
                    dict_tipos['gastos']['iva_11']+=concepto.impuesto_real
                elif concepto.tipo == HONORARIOS:
                    dict_tipos['honorarios']['sub_11']+=concepto.subtotal
                    dict_tipos['honorarios']['iva_11']+=concepto.impuesto_real
                elif concepto.tipo == RENTA:
                    dict_tipos['renta']['sub_11']+=concepto.subtotal
                    dict_tipos['renta']['iva_11']+=concepto.impuesto_real
                elif concepto.tipo == IMPUESTOS:
                    dict_tipos['impuestos']['sub_11']+=concepto.subtotal
                    dict_tipos['impuestos']['iva_11']+=concepto.impuesto_real
                elif concepto.tipo == MOV_BANCARIOS:
                    dict_tipos['mov_bancarios']['sub_11']+=concepto.subtotal
                    dict_tipos['mov_bancarios']['iva_11']+=concepto.impuesto_real
                elif concepto.tipo == ACT_FIJO:
                    dict_tipos['act_fijo']['sub_11']+=concepto.subtotal
                    dict_tipos['act_fijo']['iva_11']+=concepto.impuesto_real
                elif concepto.tipo == OTROS:
                    dict_tipos['otros']['sub_11']+=concepto.subtotal
                    dict_tipos['otros']['iva_11']+=concepto.impuesto_real
                elif concepto.tipo == SUELDOS:
                    dict_tipos['sueldos']['sub_11']+=concepto.subtotal
                    dict_tipos['sueldos']['iva_11']+=concepto.impuesto_real

            elif concepto.impuesto.porcentaje ==16:
                dict_totales['sub_16'] += concepto.subtotal
                dict_totales['iva_16'] += concepto.impuesto_real
                dict_totales['diff_16'] += concepto.diferencia_iva

                if concepto.tipo == COMPRAS:
                    dict_tipos['compras']['sub_16']+=concepto.subtotal
                    dict_tipos['compras']['iva_16']+=concepto.impuesto_real
                elif concepto.tipo == GASTOS:
                    dict_tipos['gastos']['sub_16']+=concepto.subtotal
                    dict_tipos['gastos']['iva_16']+=concepto.impuesto_real
                elif concepto.tipo == HONORARIOS:
                    dict_tipos['honorarios']['sub_16']+=concepto.subtotal
                    dict_tipos['honorarios']['iva_16']+=concepto.impuesto_real
                elif concepto.tipo == RENTA:
                    dict_tipos['renta']['sub_16']+=concepto.subtotal
                    dict_tipos['renta']['iva_16']+=concepto.impuesto_real
                elif concepto.tipo == IMPUESTOS:
                    dict_tipos['impuestos']['sub_16']+=concepto.subtotal
                    dict_tipos['impuestos']['iva_16']+=concepto.impuesto_real
                elif concepto.tipo == MOV_BANCARIOS:
                    dict_tipos['mov_bancarios']['sub_16']+=concepto.subtotal
                    dict_tipos['mov_bancarios']['iva_16']+=concepto.impuesto_real
                elif concepto.tipo == ACT_FIJO:
                    dict_tipos['act_fijo']['sub_16']+=concepto.subtotal
                    dict_tipos['act_fijo']['iva_16']+=concepto.impuesto_real
                elif concepto.tipo == OTROS:
                    dict_tipos['otros']['sub_16']+=concepto.subtotal
                    dict_tipos['otros']['iva_16']+=concepto.impuesto_real
                elif concepto.tipo == SUELDOS:
                    dict_tipos['sueldos']['sub_16']+=concepto.subtotal
                    dict_tipos['sueldos']['iva_16']+=concepto.impuesto_real


            dict_tipos['compras']['total']=dict_tipos['compras']['base_0'] + dict_tipos['compras']['sub_11'] + dict_tipos['compras']['sub_16']
            dict_tipos['gastos']['total']=dict_tipos['gastos']['base_0'] + dict_tipos['gastos']['sub_11'] + dict_tipos['gastos']['sub_16']
            dict_tipos['honorarios']['total']=dict_tipos['honorarios']['base_0'] + dict_tipos['honorarios']['sub_11'] + dict_tipos['honorarios']['sub_16']
            dict_tipos['renta']['total']=dict_tipos['renta']['base_0'] + dict_tipos['renta']['sub_11'] + dict_tipos['renta']['sub_16']
            dict_tipos['impuestos']['total']=dict_tipos['impuestos']['base_0'] + dict_tipos['impuestos']['sub_11'] + dict_tipos['impuestos']['sub_16']
            dict_tipos['mov_bancarios']['total']=dict_tipos['mov_bancarios']['base_0'] + dict_tipos['mov_bancarios']['sub_11'] + dict_tipos['mov_bancarios']['sub_16']
            dict_tipos['act_fijo']['total']=dict_tipos['act_fijo']['base_0'] + dict_tipos['act_fijo']['sub_11'] + dict_tipos['act_fijo']['sub_16']
            dict_tipos['otros']['total']=dict_tipos['otros']['base_0'] + dict_tipos['otros']['sub_11'] + dict_tipos['otros']['sub_16']
            dict_tipos['sueldos']['total']=dict_tipos['sueldos']['base_0'] + dict_tipos['sueldos']['sub_11'] + dict_tipos['sueldos']['sub_16']


            dict_totales['ret_iva'] += concepto.ret_iva
            dict_totales['ret_isr'] += concepto.ret_isr
            dict_totales['importe'] += concepto.importe
            dict_totales['bancos'] += concepto.bancos
            dict_totales['diff']   += concepto.diferencia

    dict_totales['total_acreditable'] = dict_totales['iva_11'] + dict_totales['iva_16']
    dict_totales['ded_autorizadas'] = dict_totales['base_0'] + dict_totales['sub_11'] + dict_totales['sub_16']

    dict_final = {}
    dict_final['totales'] = dict_totales
    dict_final['tipos'] = dict_tipos
    return dict_final


def resumen_cuentas(cheques, contri=None):
    if contri == None:
        cuentas = Cuenta.objects.all()
    else:
        cuentas = Cuenta.objects.filter(contri=contri)
    cuenta_list=[]
    for cuenta in cuentas:
        cuenta_dict={}
        cuenta_dict['numero'] = cuenta.numero
        cuenta_dict['banco'] = cuenta.banco.nombre
        cuenta_dict['total'] = 0
        
        for cheque in cheques.filter(cuenta=cuenta):
            cuenta_dict['total']+=cheque.get_total_conceptos()

        cuenta_list.append(cuenta_dict)
    return cuenta_list


from utils import get_next_or_previous

def concepto_anterior(request, concepto_id):
    contri = request.session['contri']
    concepto = Concepto.objects.get(id=concepto_id)
    conceptos = Concepto.objects.filter(cheque__cuenta__contri__id=contri.id).order_by('fecha_creacion')
    anterior = get_next_or_previous(conceptos, concepto, next=False)
    if anterior == None:
        if concepto.cheque.estado == 3:
            return HttpResponseRedirect('/diot/cheques/editar_rapido/%s/' % concepto.cheque.id)
        else:
            return HttpResponseRedirect('/diot/conceptos/editar/%s/' % concepto.id)
        
    if anterior.cheque.estado == 3:
        return HttpResponseRedirect('/diot/cheques/editar_rapido/%s/' % anterior.cheque.id)
    else:
        return HttpResponseRedirect('/diot/conceptos/editar/%s/' % anterior.id)




def concepto_siguiente(request, concepto_id):
    contri = request.session['contri']
    concepto = Concepto.objects.get(id=concepto_id)
    conceptos = Concepto.objects.filter(cheque__cuenta__contri__id=contri.id).order_by('fecha_creacion')
    siguiente = get_next_or_previous(conceptos, concepto, next=True)
    if siguiente == None:
        if concepto.cheque.estado == 3:
            return HttpResponseRedirect('/diot/cheques/editar_rapido/%s/' % concepto.cheque.id)
        else:
            return HttpResponseRedirect('/diot/conceptos/editar/%s/' % concepto.id)

    if siguiente.cheque.estado == 3:
        return HttpResponseRedirect('/diot/cheques/editar_rapido/%s/' % siguiente.cheque.id)
    else:
        return HttpResponseRedirect('/diot/conceptos/editar/%s/' % siguiente.id)


def tmensual_crear(request, month=None, year=None):
    contri = request.session['contri']
    f = CrearTotalForm(month=month, year=year, contri=contri)
    if request.POST:
        f = CrearTotalForm(month, year, contri, request.POST)
        if f.errors:
            return render_to_response('diot/totales/create_total.html',{'month':month, 'year':year, 'form':f}, RequestContext(request))
        else:
            cuenta = f.cleaned_data['cuenta']
            total = f.cleaned_data['total']
            month = f.cleaned_data['month']
            year = f.cleaned_data['year']

            mensual = TotalMensual()
            mensual.cuenta = cuenta
            mensual.total = total
            mensual.contri = contri
            mensual.month = month
            mensual.year = year
            mensual.save()
            if 'add_another' in request.POST:
                return HttpResponseRedirect('/diot/totales/crear/%s/%s/'%(year,month))
            else:
                return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(year,month))


    else:
        return render_to_response('diot/totales/create_total.html',{'month':month, 'year':year, 'form':f}, RequestContext(request))


def tmensual_edit(request, tmensual_id):
    contri = request.session['contri']
    tmensual = TotalMensual.objects.get(id=tmensual_id)
    f = EditarTotalForm(tmensual)

    if request.POST:
        f = EditarTotalForm(tmensual, request.POST)
        if f.errors:
            return render_to_response('diot/totales/edit_total.html',{'form':f, 'tmensual':tmensual}, RequestContext(request))
        else:
            cuenta = f.cleaned_data['cuenta']
            total = f.cleaned_data['total']
            month = f.cleaned_data['month']
            year = f.cleaned_data['year']

            tmensual.cuenta = cuenta
            tmensual.total = total
            tmensual.contri = contri
            tmensual.month = month
            tmensual.year = year
            tmensual.save()
            if 'add_another' in request.POST:
                return HttpResponseRedirect('/diot/totales/crear/%s/%s/'%(year,month))
            else:
                return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(year,month))

    else:
        return render_to_response('diot/totales/edit_total.html',{'form':f,'tmensual':tmensual}, RequestContext(request))


def tmensual_eliminar(request, tmensual_id):
    contri = request.session['contri']
    try:
        tmensual = TotalMensual.objects.get(id=tmensual_id)
        month = tmensual.month
        year = tmensual.year
    except Cheque.DoesNotExist:
        raise Http404

    if not tmensual.contri.id == contri.id:
        raise Http404

    if request.POST:
        tmensual.delete()
        return HttpResponseRedirect('/diot/cheques/fechas/%s/%s/'%(year,month))
    else:
        return render_to_response('diot/totales/eliminar_total.html',{'tmensual':tmensual}, RequestContext(request))

