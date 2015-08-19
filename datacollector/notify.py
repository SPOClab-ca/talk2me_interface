# Create functions for handling user notifications

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.db.models.query import QuerySet
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson

from datacollector.models import *
from csc2518.settings import STATIC_URL
from csc2518.settings import SUBSITE_ID

import datetime
import json


'''Return a QuerySet of the active (end date after today's date) and new (non-dismissed) notifications for a given user.
   'subject' is a db object of type Subject. If there are no results, return an empty list.'''
def get_active_new(subject):
    notif = []
    if subject and type(subject) is Subject:
        notif = Subject_Notifications.objects.filter(Q(date_end__isnull=True) | Q(date_end__gte = datetime.datetime.now().date()), subject=subject, dismissed=0)
    
    return notif
    

'''Receives a POST request with the following parameters: target_notif - either an empty array (target is ALL active and new notifications), or an array of subject_notification_id. For each target notification, set 'dismissed' flag to 1.'''
def dismiss(request):
    # Dismiss active new notifications for the currently logged on user
    json_data = {}
    json_data['status'] = 'success'
    if request.user.is_authenticated():
        try:
            s = Subject.objects.get(user_id=request.user.id)
            
            # Check which active notifications to dismiss
            if 'target_notif' in request.POST:
                target_notif = request.POST['target_notif']
                active_notifications = []
                if not target_notif: # get all active new notifications
                    active_notifications = get_active_new(s)
                else:
                    active_notifications = Subject_Notifications.objects.filter(subject_notification_id__in=target_notif)
                    
                if active_notifications:
                    active_notifications.update(dismissed=1)
                    
                return HttpResponse(json.dumps(json_data))
            else:
                json_data['status'] = 'error'
                json_data['error'] = 'Invalid request, missing parameters'
                return HttpResponse(json.dumps(json_data), status=400)
                
        except Subject.DoesNotExist:
            json_data['status'] = 'error'
            json_data['error'] = 'Invalid request, subject does not exist'
            return HttpResponse(json.dumps(json_data), status=400)
    else:
        json_data['status'] = 'error'
        json_data['error'] = 'Unauthorized'
        return HttpResponse(json_dumps(json_data), status=401)
        
        