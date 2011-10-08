from django.shortcuts import render_to_response, HttpResponseRedirect
from diot.models import Cuenta, Cheque, Proveedor, Concepto, COMPRAS, GASTOS, HONORARIOS, RENTA, IMPUESTOS, MOV_BANCARIOS, ACT_FIJO, OTROS
from empresa.models import Empresa
from django.template import RequestContext
from django.http import Http404
from reportes.forms import MesForm

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
    conceptos = Concepto.objects.filter(cheque__fecha__month=month, cheque__fecha__year=year,  cheque__cuenta__contri=contri)
    final = resumen_proveedores(conceptos)
    resumen = final['prov_list']
    totales = final['totales']
    return render_to_response('reportes/proveedores.html',{'resumen':resumen, 'empresa':empresa, 'contri':contri, 'totales':totales}, RequestContext(request))


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
            if con.impuesto == None:
                prov_dict['base_0'] += con.subtotal
            elif con.impuesto.porcentaje == 11:
                prov_dict['sub_11'] += con.subtotal
                prov_dict['iva_11'] += con.impuesto_real
            elif con.impuesto.porcentaje == 16:
                prov_dict['sub_16'] += con.subtotal
                prov_dict['iva_16'] += con.impuesto_real

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


