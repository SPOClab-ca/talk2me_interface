from django.db import connection
from django.db.models import Q, Count, Min
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from datacollector.models import *
from csc2518.settings import STATIC_URL
from csc2518.settings import SUBSITE_ID

import datetime
import notify
import numpy


# Set up mail authentication
global email_username, email_name, website_hostname
email_username = Settings.objects.get(setting_name="system_email").setting_value
email_name = Settings.objects.get(setting_name="system_email_name").setting_value
website_hostname = Settings.objects.get(setting_name="website_hostname").setting_value
website_name = Settings.objects.get(setting_name="website_name").setting_value

# Globals
global global_passed_vars, date_format, age_limit, regex_email, regex_date, colour_lookup
global_passed_vars = { "website_id": "talk2me", "website_name": website_name, "website_email": email_username }
website_root = '/'
if SUBSITE_ID: website_root += SUBSITE_ID

global DATA_ROW_SEP, DATA_COL_SEP, date_format, month_format, DAYS_PER_YEAR
DATA_ROW_SEP = "#"
DATA_COL_SEP = "|"
date_format = "%Y-%m-%d"
month_format = "%Y-%m"
DAYS_PER_YEAR = 365.2425 # average length of year taking into account leap years

    
def dashboard(request):
    is_authenticated = False
    consent_submitted = None
    demographic_submitted = None
    active_notifications = None
    adminui_data = ""
    
    if request.user.is_authenticated() and request.user.is_superuser:
        is_authenticated = True
        subject = Subject.objects.filter(user_id=request.user.id)
        today = datetime.datetime.now().date()
        
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted
            
            # Fetch all notifications that are active and have not been dismissed by the user 
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = notify.get_active_new(subject)
            
            # Get all the statistical data to be displayed in graphs and charts
            # - Number of users by gender (pie chart)
            piechart_gender = [DATA_COL_SEP.join(["Gender", "Users"])]
            piechart_gender += [DATA_COL_SEP.join([x.name, str(x.subject__count)]) for x in Gender.objects.annotate(Count('subject'))]
            adminui_data += "<input class='adminui_data' type='hidden' chart-type='pie' data-title='Number of users by gender' value='" + DATA_ROW_SEP.join(piechart_gender) + "' />"
            
            # - Number of users in different age brackets (bar graph). Bin the age in decades.
            bin_interval = 10
            min_age = 1
            max_age = 100
            age_bins = numpy.arange(min_age,max_age,bin_interval)
            age_data = [int((today - x.dob).days / DAYS_PER_YEAR) for x in Subject.objects.filter(dob__isnull=False)]
            age_data_binned = list(numpy.digitize(age_data, age_bins))
            list_bins = list(age_bins)
            # Get the number of subjects in each bin, in the format e.g.: ["1-10"|"0", "11-20"|"0", "21-30"|"5", ...]
            bargraph_age = [DATA_COL_SEP.join(["Age", "Users"])]
            bargraph_age += [DATA_COL_SEP.join([str(b) + "-" + str(b+bin_interval-1), str(age_data_binned.count(list_bins.index(b)+1))]) for b in list_bins]
            adminui_data += "<input class='adminui_data' type='hidden' chart-type='bar' data-title='Number of users by age' value='" + DATA_ROW_SEP.join(bargraph_age) + "' />"
            
            # - Number of tasks completed over time (by month since inception, where inception = first task completion date)
            truncate_date = connection.ops.date_trunc_sql('month', 'date_completed')
            completed_tasks = Session_Task.objects.filter(date_completed__isnull=False).extra({'month': truncate_date})
            tasks_by_month = completed_tasks.values('month').annotate(Count('session_task_id')).order_by('month')
            bargraph_tasks_by_month = [DATA_COL_SEP.join(["Month", "Tasks"])]
            bargraph_tasks_by_month += [DATA_COL_SEP.join([x['month'].strftime(month_format), str(x['session_task_id__count'])]) for x in tasks_by_month]
            adminui_data += "<input class='adminui_data' type='hidden' chart-type='bar' data-title='Number of tasks completed by month' value='" + DATA_ROW_SEP.join(bargraph_tasks_by_month) + "' />"
            
            
            # - Breakdown of each type of task that has been completed (task as IV and number of completions as DV)
            
            
            
        passed_vars = {'is_authenticated': is_authenticated, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications, 'user': request.user, 'adminui_data': adminui_data, 'data_row_sep': DATA_ROW_SEP, 'data_col_sep': DATA_COL_SEP }
        passed_vars.update(global_passed_vars)
        return render_to_response('datacollector/adminui.html', passed_vars, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(website_root)
    