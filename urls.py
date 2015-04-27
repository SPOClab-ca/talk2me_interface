from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'csc2518.views.home', name='home'),
    # url(r'^csc2518/', include('csc2518.foo.urls')),
    
    # Index page
    url(r'^datacollector/$', 'datacollector.views.index'),
    
    # Authentication    
    url(r'^datacollector/login$', 'datacollector.views.login'),
    url(r'^datacollector/logout$', 'datacollector.views.logout'),
    url(r'^datacollector/register$', 'datacollector.views.register'),

    # Sessions 
    url(r'^datacollector/startsession$', 'datacollector.views.startsession'),
    url(r'^datacollector/session/(?P<session_id>\d+)$', 'datacollector.views.session'),

    # Testing
    url(r'^datacollector/audiotest$', 'datacollector.views.audiotest'),
    url(r'^datacollector/results/(?P<subject_id>\d+)/$', 'datacollector.views.results'),
    
    # Miscellaneous
    url(r'^datacollector/help/$', 'datacollector.views.help'),
    url(r'^datacollector/error/(?P<error_id>\d{3})/$', 'datacollector.views.error'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
