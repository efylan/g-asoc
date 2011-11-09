from django.shortcuts import render_to_response, HttpResponseRedirect, HttpResponse
from diot.models import Cuenta, Cheque, Proveedor, Concepto, COMPRAS, GASTOS, HONORARIOS, RENTA, IMPUESTOS, MOV_BANCARIOS, ACT_FIJO, OTROS, SUELDOS, EXTRANJERO, NACIONAL, GLOBAL, COMISIONES
from empresa.models import Empresa
from django.template import RequestContext
from django.http import Http404
from reportes.forms import MesForm
import csv
from decimal import Decimal
from django.db.models import Q


EXCLUDE_LIST = [SUELDOS,IMPUESTOS,MOV_BANCARIOS]
NO_APLICABLE1 = 'no aplica'
NO_APLICABLE2 = 'noaplica'
NO_APLICABLES = ['noaplica', 'no aplica']

def index_reportes(request):
    return render_to_response('reportes/main_reportes.html',{},RequestContext(request))

def reporte_proveedor(request):
    contri = request.session['contri']
    f = MesForm()
    if request.POST:
        f = MesForm(request.POST)
        if f.errors:
            return render_to_response('reportes/proveedores_f.html',{'form':f},RequestContext(request))
        else:
            month = f.cleaned_data['month']
            year = f.cleaned_data['year']
            return core_reporte_proveedor(contri, month, year, request)
    else:
        return render_to_response('reportes/proveedores_f.html',{'form':f},RequestContext(request))


def core_reporte_proveedor(contri, month, year, request):

    empresa = Empresa.objects.all()[0]
    #cheques = Cheque.objects.filter(fecha__month=month, fecha__year=year, cuenta__contri=contri)
    conceptos_raw = Concepto.objects.filter(cheque__fecha__month=month, cheque__fecha__year=year,  cheque__cuenta__contri=contri)


    conceptos = conceptos_raw.exclude(Q(proveedor__rfc__icontains=NO_APLICABLE1) | Q(proveedor__rfc__icontains=NO_APLICABLE2) | Q(tipo__in=EXCLUDE_LIST)).order_by('proveedor')

    excluidos = conceptos_raw.filter(Q(proveedor__rfc__icontains=NO_APLICABLE1) | Q(proveedor__rfc__icontains=NO_APLICABLE2) | Q(tipo__in=EXCLUDE_LIST)).order_by('proveedor')

    final = resumen_proveedores(conceptos)
    tot_exc = resumen_totales(excluidos)
    resumen = final['prov_list']
    totales = final['totales']
    tipos = resumen_tipos(conceptos_raw)


    gran_tot = {}
    gran_tot['base_0'] = totales['base_0'] + tot_exc['base_0']
    gran_tot['sub_11'] = totales['sub_11'] + tot_exc['sub_11']
    gran_tot['sub_16'] = totales['sub_16'] + tot_exc['sub_16']
    gran_tot['iva_11'] = totales['iva_11'] + tot_exc['iva_11']
    gran_tot['iva_16'] = totales['iva_16'] + tot_exc['iva_16']
    gran_tot['ret_iva'] = totales['ret_iva'] + tot_exc['ret_iva']
    gran_tot['ret_isr'] = totales['ret_isr'] + tot_exc['ret_isr']
    gran_tot['importe'] = totales['importe'] + tot_exc['importe']
    gran_tot['descuento'] = totales['descuento'] + tot_exc['descuento']
    gran_tot['descuento_iva'] = totales['descuento_iva'] + tot_exc['descuento_iva']

    return render_to_response('reportes/proveedores.html',{'resumen':resumen, 'empresa':empresa, 'contri':contri, 'totales':totales,'excluidos':excluidos, 'tot_exc':tot_exc, 'gran_tot':gran_tot, 'tipos':tipos}, RequestContext(request))


def resumen_proveedores(conceptos):
    raw_list = conceptos.values_list('proveedor_id',flat=True).distinct()
    provs = Proveedor.objects.filter(id__in=raw_list).order_by('rfc')

    prov_list = []
    totales = {}
    totales['base_0'] = 0
    totales['sub_11'] = 0
    totales['sub_16'] = 0
    totales['iva_11'] = 0
    totales['iva_16'] = 0
    totales['ret_iva'] = 0
    totales['ret_isr'] = 0
    totales['importe'] = 0
    totales['descuento'] = 0 #?
    totales['descuento_iva'] = 0 #?
    for prov in provs:
        prov_dict={}
        conceptos_prov = conceptos.filter(proveedor=prov.id).order_by('cheque')
        prov_dict['proveedor'] = prov
        prov_dict['conceptos'] = conceptos_prov
        prov_dict['base_0'] = 0
        prov_dict['sub_11'] = 0
        prov_dict['sub_16'] = 0
        prov_dict['iva_11'] = 0
        prov_dict['iva_16'] = 0
        prov_dict['ret_iva'] = 0
        prov_dict['ret_isr'] = 0
        prov_dict['importe'] = 0
        prov_dict['descuento'] = 0 #?
        prov_dict['descuento_iva'] = 0 #?
        prov_dict['count'] = conceptos_prov.count()
        for con in conceptos_prov:
            prov_dict['base_0'] += con.exento
            if con.impuesto == None:
                prov_dict['base_0'] += con.subtotal
            elif con.impuesto.porcentaje == 11:
                prov_dict['sub_11'] += con.subtotal
                prov_dict['iva_11'] += con.impuesto_real
            elif con.impuesto.porcentaje == 16:
                prov_dict['sub_16'] += con.subtotal
                prov_dict['iva_16'] += con.impuesto_real

            prov_dict['descuento'] += con.descuento
            prov_dict['descuento_iva'] += con.iva_descuento
            prov_dict['ret_iva'] += con.ret_iva
            prov_dict['ret_isr'] += con.ret_isr
            prov_dict['importe'] += con.bancos

        totales['base_0'] += prov_dict['base_0']
        totales['sub_11'] += prov_dict['sub_11']
        totales['sub_16'] += prov_dict['sub_16']
        totales['iva_11'] += prov_dict['iva_11']
        totales['iva_16'] += prov_dict['iva_16']
        totales['ret_iva'] += prov_dict['ret_iva']
        totales['ret_isr'] += prov_dict['ret_isr']
        totales['importe'] += prov_dict['importe']
        totales['descuento'] += prov_dict['descuento'] #?
        totales['descuento_iva'] += prov_dict['descuento_iva'] #?
        prov_list.append(prov_dict)
    totales['importe_11'] = totales['sub_11'] + totales['iva_11']
    totales['importe_16'] = totales['sub_16'] + totales['iva_16']
    final_dict = {'prov_list':prov_list, 'totales':totales}
    return final_dict


def resumen_totales(conceptos):
    total_dict={}
    total_dict['base_0'] = 0
    total_dict['sub_11'] = 0
    total_dict['sub_16'] = 0
    total_dict['iva_11'] = 0
    total_dict['iva_16'] = 0
    total_dict['ret_iva'] = 0
    total_dict['ret_isr'] = 0
    total_dict['importe'] = 0
    total_dict['descuento'] = 0 #?
    total_dict['descuento_iva'] = 0 #?
    total_dict['count'] = conceptos.count()
    for con in conceptos:
        total_dict['base_0'] += con.exento
        if con.impuesto == None:
            total_dict['base_0'] += con.subtotal
        elif con.impuesto.porcentaje == 11:
            total_dict['sub_11'] += con.subtotal
            total_dict['iva_11'] += con.impuesto_real
        elif con.impuesto.porcentaje == 16:
            total_dict['sub_16'] += con.subtotal
            total_dict['iva_16'] += con.impuesto_real

        total_dict['descuento'] += con.descuento
        total_dict['descuento_iva'] += con.iva_descuento
        total_dict['ret_iva'] += con.ret_iva
        total_dict['ret_isr'] += con.ret_isr
        total_dict['importe'] += con.bancos

    return total_dict


def resumen_tipos(conceptos):
    dict_tipos={}
    dict_tipos['compras'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0,'ret_iva':0, 'ret_isr':0, 'desc':0, 'desc_iva':0}
    dict_tipos['gastos'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0,'ret_iva':0, 'ret_isr':0, 'desc':0, 'desc_iva':0}
    dict_tipos['honorarios'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0,'ret_iva':0, 'ret_isr':0, 'desc':0, 'desc_iva':0}
    dict_tipos['renta'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0,'ret_iva':0, 'ret_isr':0, 'desc':0, 'desc_iva':0}
    dict_tipos['impuestos'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0,'ret_iva':0, 'ret_isr':0, 'desc':0, 'desc_iva':0}
    dict_tipos['mov_bancarios'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0,'ret_iva':0, 'ret_isr':0, 'desc':0, 'desc_iva':0}
    dict_tipos['act_fijo'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0,'ret_iva':0, 'ret_isr':0, 'desc':0, 'desc_iva':0}
    dict_tipos['otros'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0,'ret_iva':0, 'ret_isr':0, 'desc':0, 'desc_iva':0}
    dict_tipos['sueldos'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0,'ret_iva':0, 'ret_isr':0, 'desc':0, 'desc_iva':0}
    dict_tipos['comisiones'] = {'base_0':0, 'sub_11':0, 'sub_16':0, 'iva_11':0, 'iva_16':0,'ret_iva':0, 'ret_isr':0, 'desc':0, 'desc_iva':0}


    for concepto in conceptos:
        #TODO
        if concepto.tipo == COMPRAS:
            dict_tipos['compras']['ret_iva']+=concepto.ret_iva
            dict_tipos['compras']['ret_isr']+=concepto.ret_isr
            dict_tipos['compras']['desc']+=concepto.descuento
            dict_tipos['compras']['desc_iva']+=concepto.iva_descuento
        elif concepto.tipo == GASTOS:
            dict_tipos['gastos']['ret_iva']+=concepto.ret_iva
            dict_tipos['gastos']['ret_isr']+=concepto.ret_isr
            dict_tipos['gastos']['desc']+=concepto.descuento
            dict_tipos['gastos']['desc_iva']+=concepto.iva_descuento
        elif concepto.tipo == HONORARIOS:
            dict_tipos['honorarios']['ret_iva']+=concepto.ret_iva
            dict_tipos['honorarios']['ret_isr']+=concepto.ret_isr
            dict_tipos['honorarios']['desc']+=concepto.descuento
            dict_tipos['honorarios']['desc_iva']+=concepto.iva_descuento
        elif concepto.tipo == RENTA:
            dict_tipos['renta']['ret_iva']+=concepto.ret_iva
            dict_tipos['renta']['ret_isr']+=concepto.ret_isr
            dict_tipos['renta']['desc']+=concepto.descuento
            dict_tipos['renta']['desc_iva']+=concepto.iva_descuento
        elif concepto.tipo == IMPUESTOS:
            dict_tipos['impuestos']['ret_iva']+=concepto.ret_iva
            dict_tipos['impuestos']['ret_isr']+=concepto.ret_isr
            dict_tipos['impuestos']['desc']+=concepto.descuento
            dict_tipos['impuestos']['desc_iva']+=concepto.iva_descuento
        elif concepto.tipo == MOV_BANCARIOS:
            dict_tipos['mov_bancarios']['ret_iva']+=concepto.ret_iva
            dict_tipos['mov_bancarios']['ret_isr']+=concepto.ret_isr
            dict_tipos['mov_bancarios']['desc']+=concepto.descuento
            dict_tipos['mov_bancarios']['desc_iva']+=concepto.iva_descuento
        elif concepto.tipo == ACT_FIJO:
            dict_tipos['act_fijo']['ret_iva']+=concepto.ret_iva
            dict_tipos['act_fijo']['ret_isr']+=concepto.ret_isr
            dict_tipos['act_fijo']['desc']+=concepto.descuento
            dict_tipos['act_fijo']['desc_iva']+=concepto.iva_descuento
        elif concepto.tipo == OTROS:
            dict_tipos['otros']['ret_iva']+=concepto.ret_iva
            dict_tipos['otros']['ret_isr']+=concepto.ret_isr
            dict_tipos['otros']['desc']+=concepto.descuento
            dict_tipos['otros']['desc_iva']+=concepto.iva_descuento
        elif concepto.tipo == SUELDOS:
            dict_tipos['sueldos']['ret_iva']+=concepto.ret_iva
            dict_tipos['sueldos']['ret_isr']+=concepto.ret_isr
            dict_tipos['sueldos']['desc']+=concepto.descuento
            dict_tipos['sueldos']['desc_iva']+=concepto.iva_descuento
        elif concepto.tipo == COMISIONES:
            dict_tipos['comisiones']['ret_iva']+=concepto.ret_iva
            dict_tipos['comisiones']['ret_isr']+=concepto.ret_isr
            dict_tipos['comisiones']['desc']+=concepto.descuento
            dict_tipos['comisiones']['desc_iva']+=concepto.iva_descuento


        if concepto.impuesto==None:
            if concepto.tipo == COMPRAS:
                dict_tipos['compras']['base_0']+=concepto.subtotal
                dict_tipos['compras']['base_0']+=concepto.exento
            elif concepto.tipo == GASTOS:
                dict_tipos['gastos']['base_0']+=concepto.subtotal
                dict_tipos['gastos']['base_0']+=concepto.exento
            elif concepto.tipo == HONORARIOS:
                dict_tipos['honorarios']['base_0']+=concepto.subtotal
                dict_tipos['honorarios']['base_0']+=concepto.exento
            elif concepto.tipo == RENTA:
                dict_tipos['renta']['base_0']+=concepto.subtotal
                dict_tipos['renta']['base_0']+=concepto.exento
            elif concepto.tipo == IMPUESTOS:
                dict_tipos['impuestos']['base_0']+=concepto.subtotal
                dict_tipos['impuestos']['base_0']+=concepto.exento
            elif concepto.tipo == MOV_BANCARIOS:
                dict_tipos['mov_bancarios']['base_0']+=concepto.subtotal
                dict_tipos['mov_bancarios']['base_0']+=concepto.exento
            elif concepto.tipo == ACT_FIJO:
                dict_tipos['act_fijo']['base_0']+=concepto.subtotal
                dict_tipos['act_fijo']['base_0']+=concepto.exento
            elif concepto.tipo == OTROS:
                dict_tipos['otros']['base_0']+=concepto.subtotal
                dict_tipos['otros']['base_0']+=concepto.exento
            elif concepto.tipo == SUELDOS:
                dict_tipos['sueldos']['base_0']+=concepto.subtotal
                dict_tipos['sueldos']['base_0']+=concepto.exento
            elif concepto.tipo == COMISIONES:
                dict_tipos['comisiones']['base_0']+=concepto.subtotal
                dict_tipos['comisiones']['base_0']+=concepto.exento


        elif concepto.impuesto.porcentaje==11:
            if concepto.tipo == COMPRAS:
                dict_tipos['compras']['sub_11']+=concepto.subtotal
                dict_tipos['compras']['iva_11']+=concepto.impuesto_real
                dict_tipos['compras']['base_0']+=concepto.exento
            elif concepto.tipo == GASTOS:
                dict_tipos['gastos']['sub_11']+=concepto.subtotal
                dict_tipos['gastos']['iva_11']+=concepto.impuesto_real
                dict_tipos['gastos']['base_0']+=concepto.exento
            elif concepto.tipo == HONORARIOS:
                dict_tipos['honorarios']['sub_11']+=concepto.subtotal
                dict_tipos['honorarios']['iva_11']+=concepto.impuesto_real
                dict_tipos['honorarios']['base_0']+=concepto.exento
            elif concepto.tipo == RENTA:
                dict_tipos['renta']['sub_11']+=concepto.subtotal
                dict_tipos['renta']['iva_11']+=concepto.impuesto_real
                dict_tipos['renta']['base_0']+=concepto.exento
            elif concepto.tipo == IMPUESTOS:
                dict_tipos['impuestos']['sub_11']+=concepto.subtotal
                dict_tipos['impuestos']['iva_11']+=concepto.impuesto_real
                dict_tipos['impuestos']['base_0']+=concepto.exento
            elif concepto.tipo == MOV_BANCARIOS:
                dict_tipos['mov_bancarios']['sub_11']+=concepto.subtotal
                dict_tipos['mov_bancarios']['iva_11']+=concepto.impuesto_real
                dict_tipos['mov_bancarios']['base_0']+=concepto.exento
            elif concepto.tipo == ACT_FIJO:
                dict_tipos['act_fijo']['sub_11']+=concepto.subtotal
                dict_tipos['act_fijo']['iva_11']+=concepto.impuesto_real
                dict_tipos['act_fijo']['base_0']+=concepto.exento
            elif concepto.tipo == OTROS:
                dict_tipos['otros']['sub_11']+=concepto.subtotal
                dict_tipos['otros']['iva_11']+=concepto.impuesto_real
                dict_tipos['otros']['base_0']+=concepto.exento
            elif concepto.tipo == SUELDOS:
                dict_tipos['sueldos']['sub_11']+=concepto.subtotal
                dict_tipos['sueldos']['iva_11']+=concepto.impuesto_real
                dict_tipos['sueldos']['base_0']+=concepto.exento
            elif concepto.tipo == COMISIONES:
                dict_tipos['comisiones']['sub_11']+=concepto.subtotal
                dict_tipos['comisiones']['iva_11']+=concepto.impuesto_real
                dict_tipos['comisiones']['base_0']+=concepto.exento

        elif concepto.impuesto.porcentaje ==16:

            if concepto.tipo == COMPRAS:
                dict_tipos['compras']['sub_16']+=concepto.subtotal
                dict_tipos['compras']['iva_16']+=concepto.impuesto_real
                dict_tipos['compras']['base_0']+=concepto.exento
            elif concepto.tipo == GASTOS:
                dict_tipos['gastos']['sub_16']+=concepto.subtotal
                dict_tipos['gastos']['iva_16']+=concepto.impuesto_real
                dict_tipos['gastos']['base_0']+=concepto.exento
            elif concepto.tipo == HONORARIOS:
                dict_tipos['honorarios']['sub_16']+=concepto.subtotal
                dict_tipos['honorarios']['iva_16']+=concepto.impuesto_real
                dict_tipos['honorarios']['base_0']+=concepto.exento
            elif concepto.tipo == RENTA:
                dict_tipos['renta']['sub_16']+=concepto.subtotal
                dict_tipos['renta']['iva_16']+=concepto.impuesto_real
                dict_tipos['renta']['base_0']+=concepto.exento
            elif concepto.tipo == IMPUESTOS:
                dict_tipos['impuestos']['sub_16']+=concepto.subtotal
                dict_tipos['impuestos']['iva_16']+=concepto.impuesto_real
                dict_tipos['impuestos']['base_0']+=concepto.exento
            elif concepto.tipo == MOV_BANCARIOS:
                dict_tipos['mov_bancarios']['sub_16']+=concepto.subtotal
                dict_tipos['mov_bancarios']['iva_16']+=concepto.impuesto_real
                dict_tipos['mov_bancarios']['base_0']+=concepto.exento
            elif concepto.tipo == ACT_FIJO:
                dict_tipos['act_fijo']['sub_16']+=concepto.subtotal
                dict_tipos['act_fijo']['iva_16']+=concepto.impuesto_real
                dict_tipos['act_fijo']['base_0']+=concepto.exento
            elif concepto.tipo == OTROS:
                dict_tipos['otros']['sub_16']+=concepto.subtotal
                dict_tipos['otros']['iva_16']+=concepto.impuesto_real
                dict_tipos['otros']['base_0']+=concepto.exento
            elif concepto.tipo == SUELDOS:
                dict_tipos['sueldos']['sub_16']+=concepto.subtotal
                dict_tipos['sueldos']['iva_16']+=concepto.impuesto_real
                dict_tipos['sueldos']['base_0']+=concepto.exento
            elif concepto.tipo == COMISIONES:
                dict_tipos['comisiones']['sub_16']+=concepto.subtotal
                dict_tipos['comisiones']['iva_16']+=concepto.impuesto_real
                dict_tipos['comisiones']['base_0']+=concepto.exento


    dict_tipos['compras']['subtotal']=dict_tipos['compras']['base_0'] + dict_tipos['compras']['sub_11'] + dict_tipos['compras']['sub_16']
    dict_tipos['gastos']['subtotal']=dict_tipos['gastos']['base_0'] + dict_tipos['gastos']['sub_11'] + dict_tipos['gastos']['sub_16']
    dict_tipos['honorarios']['subtotal']=dict_tipos['honorarios']['base_0'] + dict_tipos['honorarios']['sub_11'] + dict_tipos['honorarios']['sub_16']
    dict_tipos['renta']['subtotal']=dict_tipos['renta']['base_0'] + dict_tipos['renta']['sub_11'] + dict_tipos['renta']['sub_16']
    dict_tipos['impuestos']['subtotal']=dict_tipos['impuestos']['base_0'] + dict_tipos['impuestos']['sub_11'] + dict_tipos['impuestos']['sub_16']
    dict_tipos['mov_bancarios']['subtotal']=dict_tipos['mov_bancarios']['base_0'] + dict_tipos['mov_bancarios']['sub_11'] + dict_tipos['mov_bancarios']['sub_16']
    dict_tipos['act_fijo']['subtotal']=dict_tipos['act_fijo']['base_0'] + dict_tipos['act_fijo']['sub_11'] + dict_tipos['act_fijo']['sub_16']
    dict_tipos['otros']['subtotal']=dict_tipos['otros']['base_0'] + dict_tipos['otros']['sub_11'] + dict_tipos['otros']['sub_16']
    dict_tipos['sueldos']['subtotal']=dict_tipos['sueldos']['base_0'] + dict_tipos['sueldos']['sub_11'] + dict_tipos['sueldos']['sub_16']
    dict_tipos['comisiones']['subtotal']=dict_tipos['comisiones']['base_0'] + dict_tipos['comisiones']['sub_11'] + dict_tipos['comisiones']['sub_16']


    dict_tipos['compras']['total']=dict_tipos['compras']['base_0'] + dict_tipos['compras']['sub_11'] + dict_tipos['compras']['sub_16'] + dict_tipos['compras']['iva_11'] +dict_tipos['compras']['iva_16']
    dict_tipos['gastos']['total']=dict_tipos['gastos']['base_0'] + dict_tipos['gastos']['sub_11'] + dict_tipos['gastos']['sub_16'] + + dict_tipos['gastos']['iva_11'] + + dict_tipos['gastos']['iva_16']
    dict_tipos['honorarios']['total']=dict_tipos['honorarios']['base_0'] + dict_tipos['honorarios']['sub_11'] + dict_tipos['honorarios']['sub_16'] + dict_tipos['honorarios']['iva_11'] + dict_tipos['honorarios']['iva_16']
    dict_tipos['renta']['total']=dict_tipos['renta']['base_0'] + dict_tipos['renta']['sub_11'] + dict_tipos['renta']['sub_16'] + dict_tipos['renta']['iva_11'] + dict_tipos['renta']['iva_16']
    dict_tipos['impuestos']['total']=dict_tipos['impuestos']['base_0'] + dict_tipos['impuestos']['sub_11'] + dict_tipos['impuestos']['sub_16'] + dict_tipos['impuestos']['iva_11'] + dict_tipos['impuestos']['iva_16']
    dict_tipos['mov_bancarios']['total']=dict_tipos['mov_bancarios']['base_0'] + dict_tipos['mov_bancarios']['sub_11'] + dict_tipos['mov_bancarios']['sub_16'] + dict_tipos['mov_bancarios']['iva_11'] + dict_tipos['mov_bancarios']['iva_16']
    dict_tipos['act_fijo']['total']=dict_tipos['act_fijo']['base_0'] + dict_tipos['act_fijo']['sub_11'] + dict_tipos['act_fijo']['sub_16'] + dict_tipos['act_fijo']['iva_11'] + dict_tipos['act_fijo']['iva_16']
    dict_tipos['otros']['total']=dict_tipos['otros']['base_0'] + dict_tipos['otros']['sub_11'] + dict_tipos['otros']['sub_16'] + dict_tipos['otros']['iva_11'] + dict_tipos['otros']['iva_16']
    dict_tipos['sueldos']['total']=dict_tipos['sueldos']['base_0'] + dict_tipos['sueldos']['sub_11'] + dict_tipos['sueldos']['sub_16']+ dict_tipos['sueldos']['iva_11'] + dict_tipos['sueldos']['iva_16']
    dict_tipos['comisiones']['total']=dict_tipos['comisiones']['base_0'] + dict_tipos['comisiones']['sub_11'] + dict_tipos['comisiones']['sub_16']+ dict_tipos['comisiones']['iva_11'] + dict_tipos['comisiones']['iva_16']



    keys = dict_tipos.keys()
    dict_tipos['t_base0'] = 0
    dict_tipos['t_sub11'] = 0
    dict_tipos['t_iva11'] = 0
    dict_tipos['t_iva16'] = 0
    dict_tipos['t_sub16'] = 0
    dict_tipos['t_subtotal'] = 0
    dict_tipos['t_total'] = 0

    for key in keys:
        dict_tipos['t_base0'] += dict_tipos[key]['base_0']
        dict_tipos['t_sub11'] += dict_tipos[key]['sub_11']
        dict_tipos['t_sub16'] += dict_tipos[key]['sub_16']
        dict_tipos['t_iva11'] += dict_tipos[key]['iva_11']
        dict_tipos['t_iva16'] += dict_tipos[key]['iva_16']
        dict_tipos['t_subtotal'] += dict_tipos[key]['subtotal']
        dict_tipos['t_total'] += dict_tipos[key]['total']

    return dict_tipos


def generar_txt(request):
    contri = request.session['contri']
    f = MesForm()
    if request.POST:
        f = MesForm(request.POST)
        if f.errors:
            return render_to_response('reportes/gentxt_f.html',{'form':f},RequestContext(request))
        else:

            month = f.cleaned_data['month']
            year = f.cleaned_data['year']
            conceptos_raw = Concepto.objects.filter(cheque__fecha__month=month, cheque__fecha__year=year,  cheque__cuenta__contri=contri)
            #conceptos = conceptos_raw.exclude(tipo__in=EXCLUDE_LIST)
            #excluidos = conceptos_raw.filter(tipo__in=EXCLUDE_LIST).order_by('proveedor')

            conceptos = conceptos_raw.exclude(Q(proveedor__rfc__icontains=NO_APLICABLE1) | Q(proveedor__rfc__icontains=NO_APLICABLE2) | Q(tipo__in=EXCLUDE_LIST)).order_by('proveedor')

            excluidos = conceptos_raw.filter(Q(proveedor__rfc__icontains=NO_APLICABLE1) | Q(proveedor__rfc__icontains=NO_APLICABLE2) | Q(tipo__in=EXCLUDE_LIST)).order_by('proveedor')



            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(mimetype='text/csv')
            response['Content-Disposition'] = 'attachment; filename=diot_%s_%s_%s.txt' % (contri.rfc, month, year)
            writer = csv.writer(response, delimiter = '|', lineterminator="|\n")
            resumen_txt = totales_txt(conceptos)
            for fila in resumen_txt:
                writer.writerow(fila)
            return response
    else:
        return render_to_response('reportes/gentxt_f.html',{'form':f},RequestContext(request))

def totales_txt(conceptos):
    res = resumen_proveedores(conceptos)['prov_list']
    lista_diot = []
    for prov in res:
        if prov['proveedor'].tipo == EXTRANJERO:
            valor_11 = ''
            valor_16 = ''
            exento = ''
            impo_11 = Decimal(str(prov['sub_11'])).quantize(Decimal(0))
            impo_16 = Decimal(str(prov['sub_16'])).quantize(Decimal(0))
            impo_exento = Decimal(str(prov['base_0'])).quantize(Decimal(0))
            if impo_11 == 0:
                impo_11 = ''
            if impo_16 == 0:
                impo_16 = ''
            if impo_exento == 0:
                impo_exento = ''
            
        else:
            valor_11 = Decimal(str(prov['sub_11'])).quantize(Decimal(0))
            valor_16 = Decimal(str(prov['sub_16'])).quantize(Decimal(0))
            exento = Decimal(str(prov['base_0'])).quantize(Decimal(0))
            impo_11 = ''
            impo_16 = ''
            impo_exento = ''

            if valor_11 == 0:
                valor_11 = ''
            if valor_16 == 0:
                valor_16 = ''
            if exento == 0:
                exento = ''



        retencion = prov['ret_iva'] + prov['ret_isr']
        if retencion == 0:
            retencion = ''
        else:
            retencion = Decimal(str(retencion)).quantize(Decimal(0))

        iva_desc = prov['descuento_iva']
        if iva_desc == 0:
            iva_desc = ''
        else:
            iva_desc = Decimal(str(iva_desc)).quantize(Decimal(0))

        fila = [prov['proveedor'].get_tipo(), prov['proveedor'].get_operacion(), prov['proveedor'].rfc, '' ,'' ,'' ,'' , valor_16, '', '', valor_11, '', '', impo_16, '', impo_11, '', impo_exento, '', exento, retencion, iva_desc]
        lista_diot.append(fila)

    return lista_diot



#OK-Valor de los actos o actividades pagados a la tasa del 15%  16% de IVA
#Valor de los actos o actividades pagados a la tasa del 15% de IVA
#TODO?-Monto del IVA pagado no acreditable a la tasa del 15%  16%  (correspondiente en la proporcin de las deducciones autorizadas)
#OK-Valor de los actos o actividades pagados a la tasa del 10% u 11% de IVA	
#Valor de los actos o actividades pagados a la tasa del 10% de IVA
#TODO?-Monto del IVA pagado no acreditable a la tasa del 10% u 11% (correspondiente en la proporcin de las deducciones autorizadas)

#OK-Valor de los actos o actividades pagados en la importacin de bienes y servicios  a la tasa del 15%  16% de  IVA
#Monto del IVA pagado no acreditable por la importacion  a la tasa del 15%  16% (correspondiente en la proporcin de las deducciones autorizadas)
#OK-Valor de los actos o actividades pagados en la importacion de bienes y servicios a la tasa del 10% u 11% de IVA
#Monto del IVA pagado no acreditable por la importacion a la tasa del 10% u 11% (Correspondiente en la proporcion de las deducciones autorizadas
#OK-Valor de los actos o actividades pagados en la importacin de bienes y servicios por los que no se paraga el IVA (Exentos)

#TODO?-Valor de los demas actos o actividades pagados a la tasa del 0% de IVA	
#OK-Valor de los actos o actividades pagados por los que no se pagara el IVA (Exentos)	
#OK-IVA Retenido por el contribuyente	
#OK-IVA correspondiente a las devoluciones, descuentos y bonificaciones sobre compras

