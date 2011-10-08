from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    url(r'^login/$', 'gonzalez.users.views.login', name='login'),
    url(r'^logout/$', 'gonzalez.users.views.logout', name='logout'),
    url(r'^panel/$', 'gonzalez.users.views.panel', name='panel'),
    url(r'^seleccionar_contri/$', 'gonzalez.users.views.seleccionar_contri', name='seleccionar_contri'),
#    url(r'^clientes/$', 'gonzalez.clientes.views.lista_clientes', name='lista_cleintes'),
)


