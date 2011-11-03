from django import template
from diot.models import Impuesto
from empresa.models import Empresa
register = template.Library()

@register.simple_tag()
def impuestos_inputs():
    impuestos = Impuesto.objects.all()
    string = u''
    for impuesto in impuestos:
        string+='<input type="hidden" id="iva_%s" value="%s">' % (impuesto.id, impuesto.porcentaje)
    return string


@register.simple_tag()
def get_nombre_empresa():
    try:
        empresa = Empresa.objects.all()[0]
    except Empresa.DoesNotExist:
        empresa = Empresa()
    return empresa.nombre

