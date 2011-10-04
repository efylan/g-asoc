from django import template
from diot.models import Impuesto
register = template.Library()

@register.simple_tag()
def impuestos_inputs():
    impuestos = Impuesto.objects.all()
    string = u''
    for impuesto in impuestos:
        string+='<input type="hidden" id="iva_%s" value="%s">' % (impuesto.id, impuesto.porcentaje)
    return string

