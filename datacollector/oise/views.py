'''
    Views functions for OISE.
'''

import datetime
import json

from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from datacollector.models import Session, Session_Task, Subject, Subject_Bundle, Task
from datacollector.views import global_passed_vars, notify, STATIC_URL
from datacollector.constants import OISE_BUNDLE_ID
from datacollector.oise.session_helper import display_session_task_instance, submit_response
from datacollector.oise.demographics_helper import update_demographics

WEBSITE_ROOT = '/talk2me/oise'

STORY_RETELLING_TASK_ID = Task.objects.get(name_id='story_retelling_oise').task_id
READING_FLUENCY_TASK_ID = Task.objects.get(name_id='reading_fluency').task_id
PICTURE_DESCRIPTION_TASK_ID = Task.objects.get(name_id='picture_description_oise').task_id

def index(request):
    '''
        Display main page
    '''

    # User-specific variables
    is_authenticated = False
    subject_bundle = None
    is_oise_user = False
    consent_submitted = False
    demographic_submitted = False

    # Session-specific variables
    completed_sessions = None
    active_sessions = None
    has_active_session = False
    active_session_id = None

    today = datetime.datetime.now().date()

    if request.user.is_authenticated():
        is_authenticated = True
        subject = Subject.objects.get(user_id=request.user.id)

        if subject:
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted

            # Check if the user is associated with any active bundles
            subject_bundle = Subject_Bundle.objects\
                             .filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), \
                                     subject=subject, \
                                     active_startdate__lte=today)
            if subject_bundle:
                subject_bundle = subject_bundle[0]

                if subject_bundle.bundle.bundle_id == OISE_BUNDLE_ID:
                    is_oise_user = True
            completed_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=False).order_by('start_date')
            active_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=request.user.id).order_by('-start_date')
            if active_sessions:
                has_active_session = True
                active_session_id = active_sessions[0].session_id



    passed_vars = {
        'is_oise_user': is_oise_user,
        'is_authenticated': is_authenticated,
        'consent_submitted': consent_submitted,
        'demographic_submitted': demographic_submitted,
        'completed_sessions': completed_sessions,
        'active_sessions': active_sessions,
        'subject_bundle': subject_bundle,
        'has_active_session': has_active_session,
        'active_session_id': active_session_id
    }
    passed_vars.update(global_passed_vars)

    return render_to_response('datacollector/oise/main.html', passed_vars, context_instance=RequestContext(request))

def session(request, session_id):
    '''
        Display session view.
    '''

    demographic_submitted = False

    # Session-specific variables
    session_completed = False

    # Task instruction
    active_task_instruction = None
    submit_button_message = None
    active_task_instruction_audio = None

    # Task instance
    active_session_task_instance = None
    session_task_in_progress = False
    display_field = None
    response_field = None
    requires_audio = False
    is_last_task_instance = False


    if request.user.is_authenticated():

        is_authenticated = True
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted

            # Fetch all notifications that are active and have not been dismissed by the user
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = notify.get_active_new(subject)

        session = Session.objects.get(session_id=session_id)
        if session:

            if session.end_date:
                session_completed = True

            # Update the date_last_session_access for the user (this drives reminder emails)
            date_access = datetime.datetime.now()
            Subject.objects.filter(user_id=request.user.id).update(date_last_session_access=date_access)

            # If the session is active, find the first unanswered task instance to display
            active_task = None
            active_session_task_id = None

            # Initialize global vars for session page
            num_current_task = Session_Task.objects.filter(session=session, date_completed__isnull=False).count() + 1
            num_tasks = Session_Task.objects.filter(session=session).count()

            if not session.end_date:

                active_task = Session_Task.objects.filter(session=session, date_completed__isnull=True).order_by('order')
                if active_task:
                    active_task = active_task[0]
                    active_session_task_id = active_task.session_task_id
                    active_task_instruction = Task.objects.get(task_id=active_task.task_id).instruction

                    if active_task.task.task_id == READING_FLUENCY_TASK_ID:
                        submit_button_message = 'Continue story'
                        active_task_instruction_audio = ('<audio controls autoplay style=' + \
                                                         '"display:none;"><source src="%s/audio/oise/' + \
                                                         'instructions/example_instruction.mp3" ' + \
                                                         'type="audio/ogg">Your browser does not '+\
                                                         'support the audio element.</audio>') % STATIC_URL
                    elif active_task.task.task_id == PICTURE_DESCRIPTION_TASK_ID:
                        active_task_instruction_audio = ('<audio controls autoplay style=' + \
                                                         '"display:none;"><source src="%s/audio/oise/' + \
                                                         'instructions/example_instruction_pd.mp3" ' + \
                                                         'type="audio/ogg">Your browser does not ' + \
                                                         'support the audio element.</audio>') % STATIC_URL
                # If session responses are submitted, perform validation.
                # If validation passes, write them to the database and return a
                # 'success' response to the AJAX script. If validation fails,
                # return a 'fail' response to the AJAX script, along with the
                # form errors found.
                if request.method == "POST":
                    json_data = {}
                    json_data['status'] = 'fail'

                    if 'error' in request.POST:
                        form_errors = request.POST['error']

                    if 'form_type' in request.POST and request.POST['form_type'] == 'session_task_instance':
                        active_session_task_id = request.POST['session_task_id']

                        session_task_in_progress = True
                        active_session_task_instance, display_field, \
                        response_field, requires_audio, \
                        is_last_task_instance = display_session_task_instance(active_session_task_id)


                    elif 'instanceid' in request.POST:
                        json_response = submit_response(request)
                        return HttpResponse(json.dumps(json_response))
                    else:
                        submit_response(request)

                num_current_task = Session_Task.objects.filter(session=session, date_completed__isnull=False).count() + 1
                num_tasks = Session_Task.objects.filter(session=session).count()
            else:
                session_completed = True
                demographic_submitted = subject.date_demographics_submitted

            passed_vars = {
                'demographic_submitted': demographic_submitted,
                'session': session,
                'active_task': active_task,
                'active_session_task_id': active_session_task_id,
                'percentage_completion': min(100, round(num_current_task*100.0/num_tasks)),
                'session_task_in_progress': session_task_in_progress,
                'active_session_task_instance': active_session_task_instance,
                'active_task_instruction':  active_task_instruction,
                'active_task_instruction_audio': active_task_instruction_audio,
                'display_field': display_field,
                'response_field': response_field,
                'requires_audio': requires_audio,
                'is_last_task_instance': is_last_task_instance,
                'session_completed': session_completed,
                'submit_button_message': submit_button_message
            }
            passed_vars.update(global_passed_vars)
            return render_to_response('datacollector/oise/session.html', passed_vars, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(WEBSITE_ROOT)
    else:
        return HttpResponseRedirect(WEBSITE_ROOT)

def demographics(request):
    '''
        Display post-session survey.
    '''
    form_errors = []
    form_values = None
    demographic_submitted = False
    session_completed = True


    if request.method == "POST":
        if request.user.is_authenticated():

            form_errors, has_errors, form_values = update_demographics(request)
            if not has_errors:
                demographic_submitted = True
            passed_vars = {
                'form_errors': form_errors,
                'demographic_submitted': demographic_submitted,
                'session_completed': session_completed,
                'form_values': form_values
            }

            return render_to_response('datacollector/oise/session.html', passed_vars, context_instance=RequestContext(request))

    return HttpResponseRedirect(WEBSITE_ROOT)
