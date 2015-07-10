from django.conf.urls import patterns, include, url
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
    url(r'^' + settings.SUBSITE_ID + '$', 'datacollector.views.index'),
    
    # Authentication
    url(r'^' + settings.SUBSITE_ID + 'login$', 'datacollector.views.login'),
    url(r'^' + settings.SUBSITE_ID + 'logout$', 'datacollector.views.logout'),
    url(r'^' + settings.SUBSITE_ID + 'register$', 'datacollector.views.register'),
    url(r'^' + settings.SUBSITE_ID + 'activate/(?P<user_token>\w+)$', 'datacollector.views.activate'),

    # Sessions 
    url(r'^' + settings.SUBSITE_ID + 'startsession$', 'datacollector.views.startsession'),
    url(r'^' + settings.SUBSITE_ID + 'session/(?P<session_id>\d+)$', 'datacollector.views.session'),

    # Testing
    url(r'^' + settings.SUBSITE_ID + 'audiotest$', 'datacollector.views.audiotest'),
    url(r'^' + settings.SUBSITE_ID + 'results/(?P<subject_id>\d+)/$', 'datacollector.views.results'),
    
    # Miscellaneous
    url(r'^' + settings.SUBSITE_ID + 'pagetime$', 'datacollector.views.pagetime'),
    url(r'^' + settings.SUBSITE_ID + 'about/$', 'datacollector.views.about'),
    url(r'^' + settings.SUBSITE_ID + 'account/$', 'datacollector.views.account'),
    url(r'^' + settings.SUBSITE_ID + '404/$', 'datacollector.views.notfound'),
    url(r'^' + settings.SUBSITE_ID + 'error/(?P<error_id>\d{3})/$', 'datacollector.views.error'),
    url(r'^' + settings.SUBSITE_ID + 'media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    
    # API for phone system
    url(r'^' + settings.SUBSITE_ID + 'phone/session$', 'datacollector.phone.session'),
    url(r'^' + settings.SUBSITE_ID + 'phone/test$', 'datacollector.phone.test'),
    
    # Maintenance scripts
    url(r'^' + settings.SUBSITE_ID + 'maintenance/mailer/reminders$', 'datacollector.mailer.reminders'),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Uncomment the next line to enable the admin:
    url(r'^' + settings.SUBSITE_ID + 'admin/', include(admin.site.urls)),
)
