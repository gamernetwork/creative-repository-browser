from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('crb',
    # Examples:
    # url(r'^$', 'csvnbrowse.views.home', name='home'),
    # url(r'^csvnbrowse/', include('csvnbrowse.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^getthumbnail/(?P<path>.*)', 'views.getthumbnail'),
    url(r'^getfile/(?P<path>.*)', 'views.getfile'),
    url(r'^fileinfo/(?P<path>.*)', 'views.fileinfo'),
    url(r'^getconverted/(?P<path>.*)', 'views.getconverted'),
    url(r'^(?P<path>.*)', 'views.folder'),
)
