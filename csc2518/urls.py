""" Configuration file for URLs"""

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
    url(r'^' + settings.SUBSITE_ID + 'audiorecord$', 'datacollector.views.audiorecord'),

    # Testing
    url(r'^' + settings.SUBSITE_ID + 'results/(?P<subject_id>\d+)/$', 'datacollector.views.results'),

    # Miscellaneous
    url(r'^' + settings.SUBSITE_ID + 'admin$', 'datacollector.adminui.dashboard'),
    url(r'^' + settings.SUBSITE_ID + 'pagetime$', 'datacollector.views.pagetime'),
    url(r'^' + settings.SUBSITE_ID + 'about/$', 'datacollector.views.about'),
    url(r'^' + settings.SUBSITE_ID + 'account/$', 'datacollector.views.account'),
    url(r'^' + settings.SUBSITE_ID + '404/$', 'datacollector.views.notfound'),
    url(r'^' + settings.SUBSITE_ID + 'error/(?P<error_id>\d{3})/$', 'datacollector.views.error'),
    url(r'^' + settings.SUBSITE_ID + 'media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^' + settings.SUBSITE_ID + 'bundle/completion/validate$', 'datacollector.views.bundle_completion_validate'),
    url(r'^' + settings.SUBSITE_ID + 'survey/usability$', 'datacollector.views.survey_usability'),

    # API for phone system
    url(r'^' + settings.SUBSITE_ID + 'phone/status$', 'datacollector.phone.status'),
    url(r'^' + settings.SUBSITE_ID + 'phone/login$', 'datacollector.phone.login'),
    url(r'^' + settings.SUBSITE_ID + 'phone/session$', 'datacollector.phone.session'),
    url(r'^' + settings.SUBSITE_ID + 'phone/session/(?P<session_id>[0-9]+)$', 'datacollector.phone.session_id'),
    url(r'^' + settings.SUBSITE_ID + 'phone/session_task/(?P<session_task_id>[0-9]+)$', 'datacollector.phone.session_task'),
    url(r'^' + settings.SUBSITE_ID + 'phone/response$', 'datacollector.phone.response'),
    url(r'^' + settings.SUBSITE_ID + 'phone/task$', 'datacollector.phone.task'),
    url(r'^' + settings.SUBSITE_ID + 'phone/task_value$', 'datacollector.phone.task_value'),
    url(r'^' + settings.SUBSITE_ID + 'phone/difficulty_level$', 'datacollector.phone.difficulty_level'),

    # UHN-specific
    url(r'^' + settings.SUBSITE_ID + settings.UHN_STUDY + '$', 'datacollector.views.index'),
    url(r'^' + settings.SUBSITE_ID + settings.UHN_STUDY + 'login$', 'datacollector.views.login'),
    url(r'^' + settings.SUBSITE_ID + settings.UHN_STUDY + 'logout$', 'datacollector.views.logout'),
    url(r'^' + settings.SUBSITE_ID + settings.UHN_STUDY + 'register$', 'datacollector.views.register'),
    url(r'^' + settings.SUBSITE_ID + settings.UHN_STUDY + 'about/$', 'datacollector.views.about'),
    url(r'^' + settings.SUBSITE_ID + settings.UHN_STUDY + 'account/$', 'datacollector.views.account'),
    url(r'^' + settings.SUBSITE_ID + settings.UHN_STUDY + 'session/(?P<session_id>\d+)$', 'datacollector.views.session'),
    url(r'^' + settings.SUBSITE_ID + settings.UHN_STUDY + 'admin/uhn_(?P<bundle_uhn>[a-z]+)$', 'datacollector.adminui.uhn_dashboard'),
    url(r'^' + settings.SUBSITE_ID + settings.UHN_STUDY + 'admin$', 'datacollector.adminui.dashboard'),
    url(r'^' + settings.SUBSITE_ID + settings.UHN_STUDY + 'admin/uhn_(?P<bundle_uhn>[a-z]+)/(?P<user_id>\d+)$', 'datacollector.adminui.uhn_session'),

    # Notifications
    url(r'^' + settings.SUBSITE_ID + 'notify/dismiss/$', 'datacollector.notify.dismiss'),
    url(r'^' + settings.SUBSITE_ID + 'notify/view/$', 'datacollector.notify.view'),
    url(r'^' + settings.SUBSITE_ID + 'notify/generate_all_users/$', 'datacollector.notify.generate_all_users'),

    # Prizes
    url(r'^' + settings.SUBSITE_ID + 'prizes/certificate/$', 'datacollector.prizes.certificate'),

    # Maintenance scripts
    url(r'^' + settings.SUBSITE_ID + 'maintenance/mailer/reminders$', 'datacollector.mailer.reminders'),
    url(r'^' + settings.SUBSITE_ID + 'maintenance/mailer/monthlydraw$', 'datacollector.mailer.monthlydraw'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^' + settings.SUBSITE_ID + 'admin/', include(admin.site.urls)),
)
