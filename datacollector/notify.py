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

import calendar
import datetime
import json

# Set up mail authentication
global email_username, email_name, website_hostname
email_username = Settings.objects.get(setting_name="system_email").setting_value
email_name = Settings.objects.get(setting_name="system_email_name").setting_value
website_hostname = Settings.objects.get(setting_name="website_hostname").setting_value
website_name = Settings.objects.get(setting_name="website_name").setting_value

global global_passed_vars, website_root
global_passed_vars = { "website_id": "talk2me", "website_name": website_name, "website_email": email_username }
website_root = '/'
if SUBSITE_ID: website_root += SUBSITE_ID


'''Return a QuerySet of the active (end date after today's date) and new (non-dismissed) notifications for a given user.
   'subject' is a db object of type Subject. If there are no results, return an empty list.'''
def get_active_new(subject):
    notif = []
    if subject and type(subject) is Subject:
        today = datetime.datetime.now().date()
        notif = Subject_Notifications.objects.filter(Q(date_end__isnull=True) | Q(date_end__gte = today), subject=subject, dismissed=0, date_start__lte = today)
    
    return notif

def get_active(subject):
    notif = []
    if subject and type(subject) is Subject:
        today = datetime.datetime.now().date()
        notif = Subject_Notifications.objects.filter(Q(date_end__isnull=True) | Q(date_end__gte = today), subject=subject, date_start__lte = today)
    
    return notif    

'''Display all historical notifications for the currently logged in user.'''
def view(request):
    is_authenticated = False
    
    if request.user.is_authenticated():
        try:
            is_authenticated = True
            subject = Subject.objects.get(user_id=request.user.id)
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted
            
            # Fetch all notifications that are active and have not been dismissed by the user 
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = get_active_new(subject)
            
            # Get all historical notifications for the user
            today = datetime.datetime.now().date()
            all_notifications = Subject_Notifications.objects.filter(subject=subject, date_start__lte = today).order_by('-subject_notification_id')
            
            passed_vars = {'is_authenticated': is_authenticated, 'user': request.user, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications, 'all_notifications': all_notifications}
            passed_vars.update(global_passed_vars)
            return render_to_response('datacollector/notification.html', passed_vars, context_instance=RequestContext(request))
            
        except Subject.DoesNotExist:
            return HttpResponseRedirect(website_root)
    else:
        return HttpResponseRedirect(website_root)
    
    
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


'''The trigger has gone off, so check if any notifications need to be created.'''        
def generate_notifications(subject, trigger):
    if trigger == "onSessionComplete":
        # The user now has at least one fully completed session -> if 
        # there are no existing notifications that have this trigger,
        # create them.
        subject_active_notif = get_active(subject)
        active_notif_id = [n.notification_id for n in subject_active_notif]
        notif_to_create = Notification.objects.filter(notification_trigger=trigger).exclude(notification_id__in=active_notif_id)
        today = datetime.datetime.now().date()
        
        for notif in notif_to_create:
            expiry = None
            applicable = True
            
            if notif.notification_id == "monthlyprize_eligibility":
                # Eligibility for the monthly prize resets at the end of every month.
                expiry = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
                
                # Only create notifications for prizes IFF the user has signed up for prizes.
                if not subject.preference_prizes:
                    applicable = False
            
            if applicable:
                Subject_Notifications.objects.create(subject=subject, notification=notif, date_start=today, date_end=expiry, dismissed=0)

'''notif is a QuerySet of Subject_Notifications objects (optional). The QuerySet is assumed to contain only *active* subject notifications. If not provided, then ALL active notifications for the user are checked.'''
def update_notifications(subject, notif = None):
    if not notif:
        # Get all active notifications for the user (all need to be checked for updates)
        notif = get_active(subject)
    
    for n in notif:
        # Check if user still eligible for monthly prize draws
        if n.notification.notification_id == "monthlyprize_eligibility":
            today = datetime.datetime.now().date()
            if subject.preference_prizes:
                # User now wants prizes - extend eligibility to month end
                new_end_date = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
            else:
                # User doesn't want prizes anymore - stop the eligibility for prizes
                new_end_date = today
            
            n.date_end = new_end_date
            n.save()
                
def generate_all_users(request):
    json_data = {}
    json_data['status'] = 'success'
    if request.user.is_authenticated() and request.user.is_superuser:
    
        s = Subject.objects.all()
        for subj in s:
            # If the subject has at least one completed session, then generate the onSessionComplete notifications
            sess = Session.objects.filter(subject=subj)
            if sess:
                generate_notifications(subj, "onSessionComplete")        
        return HttpResponse(json.dumps(json_data))
        
    else:
        json_data['status'] = 'error'
        json_data['error'] = 'Unauthorized'
        return HttpResponse(json.dumps(json_data), status=401)