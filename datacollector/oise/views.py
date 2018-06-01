'''
    Views functions for OISE.
'''

import datetime
import json

from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.forms import UserCreationForm

from datacollector.models import Session, Session_Task, Subject, Subject_Bundle, Task, User, Bundle
from datacollector.views import global_passed_vars, notify, STATIC_URL, delete_session
from datacollector.constants import OISE_BUNDLE_ID
from datacollector.oise.session_helper import display_session_task_instance, submit_response
from datacollector.oise.demographics_helper import update_demographics, skip_demographics
from datacollector.oise.questionnaire_helper import save_questionnaire_responses
from datacollector.oise.admin_helper import get_oise_users, get_session_information, get_demographic_information, create_new_user

from csc2518.settings import SUBSITE_ID, OISE_STUDY

import session_helper

WEBSITE_ROOT = '/'
WEBSITE_ROOT += SUBSITE_ID
WEBSITE_ROOT += OISE_STUDY

STORY_RETELLING_TASK_ID = Task.objects.get(name_id='story_retelling_oise').task_id
READING_FLUENCY_TASK_ID = Task.objects.get(name_id='reading_fluency').task_id
PICTURE_DESCRIPTION_TASK_ID = Task.objects.get(name_id='picture_description_oise').task_id
WORD_SOUNDS_TASK_ID = Task.objects.get(name_id='word_sounds_oise').task_id
WORD_RECALL_TASK_ID = Task.objects.get(name_id='word_recall_oise').task_id
PUZZLE_SOLVING_TASK_ID = Task.objects.get(name_id='puzzle_solving_oise').task_id
WORD_MAP_TASK_ID = Task.objects.get(name_id='word_map_oise').task_id

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
    active_task_instruction_video = None
    active_task_instruction_audio_button = None

    # Task instance
    active_session_task_instance = None
    session_task_in_progress = False
    display_field = None
    response_field = None
    requires_audio = False
    is_last_task_instance = False
    audio_instruction_file = None
    allow_skipping = False
    hide_submit_button = False

    form_errors = None


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
            num_tasks_completed = Session_Task.objects.filter(session=session, date_completed__isnull=False).count()

            if not session.end_date:

                active_task = Session_Task.objects.filter(session=session, date_completed__isnull=True).order_by('order')
                if active_task:
                    active_task = active_task[0]
                    active_session_task_id = active_task.session_task_id
                    active_task_instruction = Task.objects.get(task_id=active_task.task_id).instruction

                    audio_file = None
                    if active_task.task.task_id == READING_FLUENCY_TASK_ID:
                        submit_button_message = 'Show me the story!'
                        audio_file = 'instructions/reading_fluency_instruction.mp3'
                        allow_skipping = True
                    elif active_task.task.task_id == PICTURE_DESCRIPTION_TASK_ID:
                        audio_file = 'instructions/picture_description_instruction.mp3'
                        allow_skipping = True
                    elif active_task.task.task_id == STORY_RETELLING_TASK_ID:
                        audio_file = 'instructions/story_retelling_instruction.mp3'
                        allow_skipping = True
                    elif active_task.task.task_id == WORD_SOUNDS_TASK_ID:
                        audio_file = 'instructions/word_sounds_instruction.mp3'
                    elif active_task.task.task_id == WORD_MAP_TASK_ID:
                        submit_button_message = "I'm ready to create my word map"
                        audio_file = 'instructions/word_map_instruction.mp3'
                        active_task_instruction_video = 'video/oise_word_map.mp4'
                    elif active_task.task.task_id == WORD_RECALL_TASK_ID:
                        submit_button_message = "I'm ready for the words"
                        audio_file = 'instructions/word_recall_instruction.mp3'
                    elif active_task.task.task_id == PUZZLE_SOLVING_TASK_ID:
                        submit_button_message = "I'm ready to solve the puzzles"
                        audio_file = 'instructions/puzzle_solving_instruction.mp3'
                    if audio_file:
                        active_task_instruction_audio = ('<audio controls autoplay style=' + \
                                                        '"display:none;" id="instructionAudio"><source src="%s/audio/oise/%s" ' + \
                                                        'type="audio/ogg">Your browser does not ' + \
                                                        'support the audio element.</audio>') % (STATIC_URL, audio_file)
                        active_task_instruction_audio_button = '<span onclick="document.getElementById(\'instructionAudio\').play();"><i class="fas fa-volume-up"></i></span>'
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
                        is_last_task_instance, audio_instruction_file, hide_submit_button = display_session_task_instance(active_session_task_id)

                    elif 'instanceid' in request.POST:
                        json_response = submit_response(request)
                        if json_response['status'] == 'success':
                            return HttpResponse(json.dumps(json_response))
                        else:
                            form_errors = json_response['error']
                    else:
                        json_response = submit_response(request)
                        if 'error' in json_response:
                            form_errors = json_response['error']

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
                'session_task_in_progress': session_task_in_progress,
                'active_session_task_instance': active_session_task_instance,
                'active_task_instruction':  active_task_instruction,
                'active_task_instruction_audio': active_task_instruction_audio,
                'active_task_instruction_video': active_task_instruction_video,
                'display_field': display_field,
                'response_field': response_field,
                'requires_audio': requires_audio,
                'is_last_task_instance': is_last_task_instance,
                'session_completed': session_completed,
                'submit_button_message': submit_button_message,
                'form_errors': form_errors,
                'demographics_type': 'general',
                'audio_instruction_file': audio_instruction_file,
                'allow_skipping': allow_skipping,
                'hide_submit_button': hide_submit_button,
                'total_num_tasks': num_tasks,
                'num_tasks_completed': num_tasks_completed,
                'percentage_completion': float(num_tasks_completed) / num_tasks * 100.0,
                'task_counter': num_current_task,
                'active_task_instruction_audio_button': active_task_instruction_audio_button
            }
            passed_vars.update(global_passed_vars)
            return render_to_response('datacollector/oise/session.html', passed_vars, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(WEBSITE_ROOT)
    else:
        return HttpResponseRedirect(WEBSITE_ROOT)

def demographics(request):
    '''
        Display demographics survey, to be completed before starting any session.
    '''
    form_errors = []
    form_values = None
    demographics_type = 'general'
    demographics_submitted = False

    if request.user.is_authenticated():
        if request.method == "POST":
            if 'skip_demographics' in request.POST:
                skip_demographics(request)
                return HttpResponse(json.dumps({'status': 'success'}))
            else:
                form_errors, _, \
                    form_values, demographics_type, \
                    demographics_submitted = update_demographics(request)
            passed_vars = {
                'form_errors': form_errors,
                'demographic_submitted': demographics_submitted,
                'form_values': form_values,
                'demographics_type': demographics_type
            }
            if demographics_submitted:
                # Redirect to the newly-created session
                subject = Subject.objects.get(user_id=request.user.id)
                latest_session = Session.objects.filter(subject=subject, end_date__isnull=True).order_by('start_date')[0]
                return HttpResponseRedirect(WEBSITE_ROOT + 'session/' + str(latest_session.session_id))

            return render_to_response('datacollector/oise/session.html', passed_vars, context_instance=RequestContext(request))
        elif request.method == "GET":
            passed_vars = {
                'demographics_type': 'general'
            }
            passed_vars.update(global_passed_vars)
            return render_to_response('datacollector/oise/session.html', \
                                      passed_vars, \
                                      context_instance=RequestContext(request))
    return HttpResponseRedirect(WEBSITE_ROOT)

def questionnaire(request):
    '''
        Display post-session survey.
    '''
    form_errors = []
    form_values = None

    if request.user.is_authenticated():
        if request.method == "POST":
            session_id = int(request.POST['session_id'])
            session = Session.objects.get(session_id=session_id)
            form_errors, form_values = save_questionnaire_responses(request)
            if form_errors:
                questionnaire_submitted = False
            else:
                questionnaire_submitted = True
            passed_vars = {
                'form_errors': form_errors,
                'form_values': form_values,
                'session': session,
                'session_completed': True,
                'questionnaire_submitted': questionnaire_submitted,
            }
            passed_vars.update(global_passed_vars)
            return render_to_response('datacollector/oise/session.html', passed_vars, context_instance=RequestContext(request))

def about(request):
    is_authenticated = False
    active_notifications = None
    consent_submitted = False
    demographic_submitted = False

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

    passed_vars = {
        'is_authenticated': is_authenticated,
        'user': request.user,
        'consent_submitted': consent_submitted,
        'demographic_submitted': demographic_submitted,
        'active_notifications': active_notifications,
        }
    passed_vars.update(global_passed_vars)
    return render_to_response('datacollector/oise/about.html', passed_vars, context_instance=RequestContext(request))

def admin(request):
    """
    Admin view.
        :param request:
    """
    if request.user.is_authenticated() and request.user.is_superuser:

        if request.method == 'POST':
            form_type = request.POST['form_type']
            if form_type == 'create_user_oise':
                user_created = create_new_user(request)

                if not user_created:
                    return HttpResponseRedirect(WEBSITE_ROOT + 'error')
        bundle = Bundle.objects.get(name_id='oise')
        oise_users = get_oise_users()

        passed_vars = {
            'bundle': bundle,
            'oise_users': oise_users,
            'form': UserCreationForm()
            }
        passed_vars.update(global_passed_vars)
        return render_to_response('datacollector/oise/admin.html', passed_vars, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(WEBSITE_ROOT)

def admin_view_user(request, subject_id):
    """
    Admin view for given user
        :param request:
        :param subject_id:
    """
    if request.user.is_authenticated() and request.user.is_superuser:

        if request.method == "POST":
            form_type = request.POST['form_type']

            if form_type == 'delete_session':
                session_id = request.POST['session_id']
                session_id_check = request.POST['session_id_check']
                if session_id_check == session_id:
                    delete_session(session_id)

        sessions = get_session_information(subject_id)
        username = User.objects.get(id=subject_id).username
        demographics = get_demographic_information(subject_id)
        passed_vars = {
            'subject_id': subject_id,
            'username': username,
            'sessions': sessions,
            'demographics': demographics,
            'view_session_information': True
        }
        passed_vars.update(global_passed_vars)
        return render_to_response('datacollector/oise/admin.html', passed_vars, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(WEBSITE_ROOT)

def error(request):
    """
    Redirect to generic error page
        :param request:
    """
    return render_to_response('datacollector/oise/error.html', global_passed_vars, context_instance=RequestContext(request))