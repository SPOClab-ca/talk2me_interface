""" adminui.py """

import datetime
import notify
import numpy

from django.db import connection
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from datacollector.models import (Bundle, Gender, Session, Session_Task, Session_Task_Instance,
                                  Session_Task_Instance_Value, Session_Type, Settings, Subject, Subject_Bundle, 
                                  Task, User)
from datacollector.views import generate_session, delete_session

from csc2518.settings import STATIC_URL
from csc2518.settings import SUBSITE_ID

# Set up mail authentication
global email_username, email_name, website_hostname
email_username = Settings.objects.get(setting_name="system_email").setting_value
email_name = Settings.objects.get(setting_name="system_email_name").setting_value
website_hostname = Settings.objects.get(setting_name="website_hostname").setting_value
website_name = Settings.objects.get(setting_name="website_name").setting_value

# Globals
global global_passed_vars, date_format, age_limit, regex_email, regex_date, colour_lookup
global_passed_vars = {
    "website_id": "talk2me",
    "website_name": website_name,
    "website_email": email_username
}
website_root = '/'
if SUBSITE_ID: website_root += SUBSITE_ID

global DATA_ROW_SEP, DATA_COL_SEP, date_format, month_format, DAYS_PER_YEAR
DATA_ROW_SEP = "#"
DATA_COL_SEP = "|"
date_format = "%Y-%m-%d"
month_format = "%Y-%m"
DAYS_PER_YEAR = 365.2425 # average length of year taking into account leap years

UHN_NUM_SESSIONS = 7
DURATION_BETWEEN_SESSIONS = datetime.timedelta(days=31)

def uhn_create_sessions(subject_id, bundle):
    '''
        Generate 7 sessions and specify start dates (spaced one month apart).
    '''

    today = datetime.datetime.now().date()

    subject = Subject.objects.get(user_id=subject_id)

    if bundle.name_id == 'uhn_web':
        session_type = Session_Type.objects.get(name='website')
    elif bundle.name_id == 'uhn_phone':
        session_type = Session_Type.objects.get(name='phone')

    # Call generate_session in views.py 7 times
    for _ in range(UHN_NUM_SESSIONS):
        generate_session(subject, session_type)

    start_dates = [today] * UHN_NUM_SESSIONS

    for idx in range(UHN_NUM_SESSIONS):
        if idx == 0:
            continue
        start_dates[idx] = start_dates[idx-1] + DURATION_BETWEEN_SESSIONS

    sessions = Session.objects.filter(subject_id=subject_id)

    for idx, session in enumerate(sessions):
        session_id = session.session_id
        Session.objects.filter(session_id=session_id).update(start_date=start_dates[idx])

def uhn_delete_session(session_id):
    '''
        Delete session.
    '''
    return delete_session(session_id)

def uhn_consent_submitted(subject_id, alternate_decision_maker):
    '''
        Update user from admin dashboard when consent is given.
    '''

    today = datetime.datetime.now().date()

    # Assign a date to consent submitted
    Subject.objects.filter(user_id=subject_id).update(date_consent_submitted=today)

    # Update alternate decision maker flag if necessary
    if alternate_decision_maker:
        Subject.objects.filter(user_id=subject_id).update(consent_alternate=1)

def uhn_update_phone_pin(subject_id, phone_pin):
    '''
        Update phone_pin for subject
    '''

    if len(str(phone_pin)):
        Subject.objects.filter(user_id=subject_id).update(phone_pin=phone_pin)
        return True
    else:
        return False

def uhn_session(request, bundle_uhn, user_id):
    '''
        Function for admin dashboard specific to UHN studies.
    '''

    is_authenticated = False
    bundle = None
    subject = None
    sessions = []
    session_deleted = False
    phone_pin_updated = False

    if request.user.is_authenticated() and request.user.is_superuser:

        is_authenticated = True
        bundle = Bundle.objects.get(name_id=('uhn_%s' % bundle_uhn))
        subject = Subject.objects.get(user_id=user_id)

        if request.method == 'POST':
            form_type = request.POST['form_type']

            if form_type == 'delete_session':
                session_id = request.POST['session_id']
                session_id_check = request.POST['session_id_check']
                if session_id_check == session_id:
                    session_deleted = uhn_delete_session(session_id)
                else:
                    session_deleted = False

            elif form_type == 'update_phone_pin':
                phone_pin = request.POST['phone_pin']
                if phone_pin:
                    phone_pin_updated = uhn_update_phone_pin(subject.user_id, phone_pin)
                else:
                    phone_pin_updated = False

        sessions_from_db = Session.objects.filter(subject_id=user_id)

        for session in sessions_from_db:
            session_tasks = []
            session_tasks_from_db = Session_Task.objects.filter(session_id=session.session_id)

            for session_task in session_tasks_from_db:
                session_task_values = []
                session_task_instances = Session_Task_Instance.objects.filter(session_task_id=session_task.session_task_id)

                for session_task_instance in session_task_instances:
                    session_task_instance_values = Session_Task_Instance_Value.objects.filter(session_task_instance_id=session_task_instance.session_task_instance_id)
                    for session_task_instance_value in session_task_instance_values:
                        session_task_values.append({
                            'value': session_task_instance_value.value,
                            'difficulty': session_task_instance_value.difficulty_id
                        })

                session_tasks.append({
                    'task': session_task.task.name,
                    'date_completed': session_task.date_completed,
                    'total_time': session_task.total_time,
                    'task_instances': session_task_values
                    })

            sessions.append({
                'session_id': session.session_id,
                'start_date': session.start_date,
                'end_date': session.end_date,
                'session_tasks': session_tasks
                })


        passed_vars = {
            'is_authenticated': is_authenticated,
            'bundle': bundle,
            'subject': subject,
            'sessions': sessions,
            'session_deleted': session_deleted,
            'phone_pin_updated': phone_pin_updated,
            'username': User.objects.get(id=subject.user_id).username
        }
        passed_vars.update(global_passed_vars)

        return render_to_response('datacollector/uhn/adminui_sessions.html', passed_vars, context_instance=RequestContext(request))
    return HttpResponseRedirect(website_root)


def uhn_dashboard(request, bundle_uhn):
    '''
        Function for admin dashboard specific to UHN studies.
    '''

    is_authenticated = False
    bundle = None
    subject_bundle_users = []
    subjects = []

    if request.user.is_authenticated() and request.user.is_superuser:

        bundle = Bundle.objects.get(name_id=('uhn_%s' % bundle_uhn))

        if request.method == 'POST':
            form_type = request.POST['form_type']

            if form_type == 'consent':
                consent_submitted = True if 'consent_submitted' in request.POST else False
                alternate_decision_maker = True if 'is_alternate_decision_maker' in request.POST else False
                if consent_submitted:
                    subject_id = request.POST['subject_id']
                    uhn_consent_submitted(subject_id, alternate_decision_maker)

            elif form_type == 'sessions':
                subject_id = request.POST['subject_id']
                uhn_create_sessions(subject_id, bundle)

        is_authenticated = True

        subject_bundle_users = Subject_Bundle.objects.filter(bundle=bundle)
        bundle_subjects = [subject_bundle_user.subject for subject_bundle_user in subject_bundle_users]

        is_sessions_created = []
        for bundle_subject in bundle_subjects:
            sessions_per_subject = Session.objects.filter(subject_id=bundle_subject.user_id)
            if len(sessions_per_subject) > 0:
                is_sessions_created += [True]
            else:
                is_sessions_created += [False]


        for bundle_subject, sessions_created in zip(bundle_subjects, is_sessions_created):
            subjects.append({
                'sessions_created': sessions_created,
                'user_id': bundle_subject.user_id,
                'date_consent_submitted': bundle_subject.date_consent_submitted,
                'consent_alternate': bundle_subject.consent_alternate
                })

        passed_vars = {
            'is_authenticated': is_authenticated,
            'bundle': bundle,
            'subject_bundle_users': subject_bundle_users,
            'subjects': subjects
        }

        passed_vars.update(global_passed_vars)
        return render_to_response('datacollector/uhn/adminui.html', passed_vars, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(website_root)

def dashboard(request):
    '''
        Function for general admin dashboard.
    '''

    is_authenticated = False
    consent_submitted = None
    demographic_submitted = None
    active_notifications = None
    adminui_data = ""
    longitudinal_data = ""
    bundles = []

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
            age_bins = numpy.arange(min_age, max_age, bin_interval)
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


            # - Breakdown of each type of task that has been completed (task as IV and number of completions as DV) - pie chart
            completed_tasks = Session_Task.objects.filter(date_completed__isnull=False)
            tasks_by_type = completed_tasks.values('task__name').annotate(Count('session_task_id')).order_by('task__name')
            piechart_tasks_by_type = [DATA_COL_SEP.join(["Task Type", "Tasks"])]
            piechart_tasks_by_type += [DATA_COL_SEP.join([x['task__name'], str(x['session_task_id__count'])]) for x in tasks_by_type]
            adminui_data += "<input class='adminui_data' type='hidden' chart-type='bar' data-title='Number of tasks completed by type' value='" + DATA_ROW_SEP.join(piechart_tasks_by_type) + "' />"

            # Show the avg number of completed samples per subject, for each task and overall
            num_samples_by_task_subject = Session_Task.objects.filter(date_completed__isnull=False).values('task', 'session__subject').annotate(Count('session_task_id'))
            longitudinal_data = "<thead><tr><th>Task ID</th><th>Task Name</th><th>No. samples</th><th>No. subjects</th><th>Avg no. samples per subject per task</th></tr></thead><tbody>"
            overall_avg_samples_per_subject = [0, 0]
            for task in Task.objects.filter(is_active=1).order_by('task_id'):
                total_task_samples = sum([elem['session_task_id__count'] for elem in num_samples_by_task_subject if elem['task'] == task.task_id])
                total_task_subjects = len([elem for elem in num_samples_by_task_subject if elem['task'] == task.task_id])
                overall_avg_samples_per_subject[0] += total_task_samples
                overall_avg_samples_per_subject[1] += total_task_subjects
                if total_task_subjects > 0:
                    avg_samples_per_subject = total_task_samples * 1.0 / total_task_subjects
                else:
                    avg_samples_per_subject = 0
                longitudinal_data += "<tr><td>" + str(task.task_id) + "</td><td>" + task.name + "</td><td>" + str(total_task_samples) + "</td><td>" + str(total_task_subjects) + "</td><td>" + "%.2f" % avg_samples_per_subject + "</td></tr>"
            if overall_avg_samples_per_subject[1] > 0:
                overall_avg = overall_avg_samples_per_subject[0] * 1.0 / overall_avg_samples_per_subject[1]
            else:
                overall_avg = 0
            longitudinal_data += "<tr><td colspan='2'>TOTALS</td><td>" + str(overall_avg_samples_per_subject[0]) + "</td><td></td><td>" + "%.2f" % overall_avg + "</td></tr>"
            longitudinal_data += "</tbody>"

            users_with_session = len(Session.objects.filter(end_date__isnull=False).values('subject').distinct())
            users_with_session_task = len(Session_Task.objects.filter(date_completed__isnull=False).values('session__subject').distinct())
            users_with_active_session = len(Session.objects.filter(end_date__isnull=True).values('subject').distinct())
            users_with_longitudinal = []
            for task_subject in [elem for elem in num_samples_by_task_subject if elem['session_task_id__count'] > 1]:
                s = task_subject['session__subject']
                if s not in users_with_longitudinal:
                    users_with_longitudinal += [s]
            users_with_longitudinal = len(users_with_longitudinal)

            bundles = Bundle.objects.all()


        passed_vars = {
            'is_authenticated': is_authenticated, 'consent_submitted': consent_submitted,
            'demographic_submitted': demographic_submitted,
            'active_notifications': active_notifications, 'user': request.user,
            'adminui_data': adminui_data, 'data_row_sep': DATA_ROW_SEP,
            'data_col_sep': DATA_COL_SEP, 'longitudinal_data': longitudinal_data,
            'users_with_session': users_with_session,
            'users_with_session_task': users_with_session_task,
            'users_with_active_session': users_with_active_session,
            'users_with_longitudinal': users_with_longitudinal, 'bundles': bundles
        }
        passed_vars.update(global_passed_vars)
        return render_to_response('datacollector/adminui.html', passed_vars, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(website_root)
