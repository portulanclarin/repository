from django.conf.urls.defaults import patterns

urlpatterns = patterns('metashare.oaipmh.views',
        (r'^$', 'oaipmh_view'),
        (r'^harvest/$', 'harvest'),
        (r'^expose/$', 'expose'),
        )
