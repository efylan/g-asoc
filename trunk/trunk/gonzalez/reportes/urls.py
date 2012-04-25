from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'gonzalez.reportes.views.index_reportes', name='reportes'),    
    url(r'^proveedores/$', 'gonzalez.reportes.views.reporte_proveedor', name='reporte_prov'),
    url(r'^contribuyentes/$', 'gonzalez.reportes.views.reporte_contri', name='reporte_contri'),
    url(r'^bancos/$', 'gonzalez.reportes.views.reporte_bancos', name='reporte_bancos'),
    url(r'^generar_txt/$', 'gonzalez.reportes.views.generar_txt', name='gen_txt'),

)
