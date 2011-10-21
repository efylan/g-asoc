from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    url(r'^cuentas/$', 'gonzalez.diot.views.cuentas_lista', name='cuentas_lista'),
    url(r'^cuentas/crear/$', 'gonzalez.diot.views.cuentas_crear', name='cuentas_crear'),

    url(r'^proveedores/consultar/$', 'gonzalez.diot.views.proveedores_consultar', name='cheques_crear'),

    url(r'^cheques/$', 'gonzalez.diot.views.cheques_lista', name='cheques_lista'),
    url(r'^cheques/fechas/$', 'gonzalez.diot.views.seleccionar_fecha', name='cheques_fechas'),
    url(r'^cheques/fechas/(?P<year>\d+)/(?P<month>\d+)/$', 'gonzalez.diot.views.cheques_mes', name='cheques_mes'),
    url(r'^cheques/crear/$', 'gonzalez.diot.views.cheques_crear', name='cheques_crear'),
    url(r'^cheques/crear_rapido/$', 'gonzalez.diot.views.cheques_crear_rapido', name='cheques_crear_rapido'),
    url(r'^cheques/(?P<cheque_id>\d+)/agregar_concepto/$', 'gonzalez.diot.views.agregar_concepto', name='agregar_concepto'),
    url(r'^cheques/editar_rapido/(?P<cheque_id>\d+)/$', 'gonzalez.diot.views.editar_rapido', name='editar_rapido'),
    url(r'^cheques/editar/(?P<cheque_id>\d+)/$', 'gonzalez.diot.views.editar_cheque', name='editar_cheque'),
    url(r'^cheques/eliminar/(?P<cheque_id>\d+)/$', 'gonzalez.diot.views.eliminar_cheque', name='eliminar_cheque'),

    url(r'^conceptos/editar/(?P<concepto_id>\d+)/$', 'gonzalez.diot.views.editar_concepto', name='editar_concepto'),
    url(r'^conceptos/eliminar/(?P<concepto_id>\d+)/$', 'gonzalez.diot.views.eliminar_concepto', name='eliminar_concepto'),
    url(r'^conceptos/siguiente/(?P<concepto_id>\d+)/$', 'gonzalez.diot.views.concepto_siguiente', name='eliminar_concepto'),
    url(r'^conceptos/anterior/(?P<concepto_id>\d+)/$', 'gonzalez.diot.views.concepto_anterior', name='eliminar_concepto'),


#    url(r'^clientes/$', 'gonzalez.clientes.views.lista_clientes', name='lista_cleintes'),
)


