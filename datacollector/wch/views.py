'''
    Views functions for OISE.
'''

import datetime
import json
import re

from django.db.models import Q, Count
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login as auth_login

from datacollector.models import Country, Dementia_Type, Education_Level, Ethnicity, Gender, Language, Language_Level, Session, Session_Task, Subject, Subject_Bundle, Subject_Dementia_Type, Subject_Ethnicity, Subject_Gender, Subject_Language, Bundle, Session_Task_Instance
from datacollector.forms import LoginForm
from datacollector.views import global_passed_vars, notify

from csc2518.settings import SUBSITE_ID, WCH_STUDY

from datacollector.session_helper import get_active_task, get_active_task_instances, get_display, submit_response

date_format = "%Y-%m-%d"
age_limit = 18
regex_email = re.compile(r"[^@]+@[^@]+\.[^@]+")
regex_date = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")

WEBSITE_ROOT = '/'
WEBSITE_ROOT += SUBSITE_ID

WCH_WEBSITE_ROOT = WEBSITE_ROOT + WCH_STUDY

WCH_WEB_BUNDLE = Bundle.objects.get(name_id='wch_web')
WCH_PHONE_BUNDLE = Bundle.objects.get(name_id='wch_phone')

def index(request):
    '''
        Display main page
    '''

    # User-specific variables
    is_authenticated = False
    subject_bundle = None
    is_wch_user = False
    consent_submitted = False

    # Demographics variables
    demographic_submitted = False
    gender_options = []
    language_options = []
    language_other = []
    language_fluency_options = []
    ethnicity_options = []
    education_options = []
    dementia_options = []
    country_res_options = []
    form_languages_fluency = []
    form_languages_other_fluency = []
    form_errors = []

    # Session-specific variables
    completed_sessions = None
    active_sessions = None
    pending_sessions = None

    today = datetime.datetime.now().date()
    cutoff_date = today + datetime.timedelta(days=1)

    if request.user.is_authenticated():
        is_authenticated = True
        user_id = request.user.id

        if request.method == 'POST':
            date_submitted = datetime.datetime.now()
            form_type = request.POST['form_type']

            if form_type == 'demographic':

                # Perform form validation first
                selected_gender = ""
                if 'gender' not in request.POST:
                    form_errors += ['You did not specify your gender.']
                else:
                    selected_gender = Gender.objects.filter(gender_id=request.POST['gender'])
                    if selected_gender:
                        selected_gender = selected_gender[0]

                selected_dob = ""
                if 'dob' not in request.POST or not request.POST['dob']:
                    form_errors += ['You did not specify your date of birth.']
                else:
                    selected_dob = request.POST['dob']
                    if not regex_date.match(selected_dob):
                        form_errors += ['The date of birth you specified is invalid (please enter in the format YYYY-MM-DD).']
                    else:
                        d1 = datetime.datetime.strptime(selected_dob, date_format)
                        d2 = datetime.datetime(d1.year + age_limit, d1.month, d1.day)
                        today = datetime.datetime.now()
                        delta = today - d2
                        if delta.days < 0:
                            form_errors += ['To participate in this study you must be at least 18 years of age.']

                if 'ethnicity' not in request.POST:
                    form_errors += ['You did not specify your ethnicity.']
                else:
                    response_ethnicity = request.POST.getlist('ethnicity')
                    for i in range(len(response_ethnicity)):
                        selected_ethnicity = Ethnicity.objects.filter(ethnicity_id=response_ethnicity[i])
                        if not selected_ethnicity:
                            form_errors += ['You have specified an invalid category for ethnicity.']


                # Get the fluency for each of the languages specified
                if 'language_other' in request.POST:
                    response_languages_other = request.POST.getlist('language_other')
                    for i in range(len(response_languages_other)):
                        if 'other_fluency_' + str(i+1) not in request.POST:
                            form_languages_other_fluency += [""]
                        else:
                            form_languages_other_fluency += [request.POST['other_fluency_' + str(i+1)]]


                if 'language' not in request.POST and ('language_other' not in request.POST or not [x for x in request.POST.getlist('language_other') if x]):
                    form_errors += ['You did not specify any languages you can communicate in.']
                else:
                    # Check that English has been selected as a spoken language
                    # Find ID of English language in db and compare to form inputs
                    response_languages = request.POST.getlist('language')

                    required_lang = "English"
                    english_lang = Language.objects.filter(name=required_lang)[0].language_id
                    if str(english_lang) not in response_languages:
                        form_errors += ['You did not specify any language proficiency in ' + required_lang + '. This is mandatory for participation, since this website is only available in ' + required_lang + '.']
                    else:
                        for i in range(len(response_languages)):
                            # - check that the selected languages are valid
                            selected_language = Language.objects.filter(language_id=response_languages[i])
                            if not selected_language:
                                form_errors += ['The language you have selected (' + str(response_languages[i]) + ') is invalid.']
                            else:
                                selected_language = selected_language[0]
                                # - check that level of fluency has been selected for each language
                                if 'language_fluency_' + str(response_languages[i]) not in request.POST:
                                    form_errors += ['You did not specify your level of fluency in ' + selected_language.name + '.']
                                    form_languages_fluency += [""]
                                else:
                                    form_languages_fluency += [request.POST['language_fluency_' + str(response_languages[i])] ]

                        response_languages_other = request.POST.getlist('language_other')
                        for i in range(len(response_languages_other)):
                            if response_languages_other[i]:
                                # - check that the selected languages are valid
                                selected_language = Language.objects.filter(language_id=response_languages_other[i])
                                if not selected_language:
                                    form_errors += ['The language you have selected (' + str(response_languages_other[i]) + ') is invalid.']
                                else:
                                    selected_language = selected_language[0]
                                    # - check that level of fluency has been selected for each language
                                    if 'other_fluency_' + str(i+1) not in request.POST:
                                        form_errors += ['You did not specify your level of fluency in ' + selected_language.name + '.']

                if 'education_level' not in request.POST:
                    form_errors += ['You did not specify your education level.']

                if 'dementia_med' not in request.POST:
                    form_errors += ['You did not specify whether you are currently take any medications for dementia.']

                if 'smoking' not in request.POST:
                    form_errors += ['You did not specify whether you are a regular smoker.']

                response_country_origin = ""
                if 'country_origin' not in request.POST or not request.POST['country_origin']:
                    form_errors += ['You did not specify the country you were born in.']
                else:
                    response_country_origin = Country.objects.filter(country_id=request.POST['country_origin'])
                    if not response_country_origin:
                        form_errors += ['You specified an invalid country of birth.']
                    else:
                        response_country_origin = response_country_origin[0]

                response_country_res = ""
                if 'country_res' not in request.POST or not request.POST['country_res']:
                    form_errors += ['You did not specify the country you currently reside in.']
                else:
                    response_country_res = Country.objects.filter(country_id=request.POST['country_res'])
                    if not response_country_res:
                        form_errors += ['You specified an invalid country of residence.']
                    else:
                        response_country_res = response_country_res[0]


                if not form_errors:
                    # Gender
                    Subject.objects.filter(user_id=request.user.id).update(gender=selected_gender)
                    gender_name = None
                    subject = Subject.objects.filter(user_id=request.user.id)
                    if subject:
                        subject = subject[0]
                    if 'gender_detail_o' in request.POST:
                        gender_name = request.POST['gender_detail_o']

                    subject_gender_exists = Subject_Gender.objects.filter(subject=subject, gender_id=selected_gender.gender_id)
                    if not subject_gender_exists:
                        Subject_Gender.objects.create(subject=subject,
                                                      gender_id=selected_gender.gender_id,
                                                      gender_name=gender_name)

                    # DOB
                    Subject.objects.filter(user_id=request.user.id).update(dob=selected_dob)

                    # Ethnicity
                    response_ethnicity = request.POST.getlist('ethnicity')
                    for i in range(len(response_ethnicity)):
                        selected_ethnicity = Ethnicity.objects.get(ethnicity_id=response_ethnicity[i])
                        subject = Subject.objects.filter(user_id=request.user.id)
                        if subject:
                            subject = subject[0]

                        ethnicity_exists = Subject_Ethnicity.objects.filter(subject=subject, ethnicity=selected_ethnicity)
                        if not ethnicity_exists:
                            Subject_Ethnicity.objects.create(subject=subject, ethnicity=selected_ethnicity)

                    # Languages
                    if 'language' in request.POST:
                        response_languages = request.POST.getlist('language')
                        for i in range(len(response_languages)):

                            selected_language = Language.objects.get(language_id=response_languages[i])
                            subject = Subject.objects.filter(user_id=request.user.id)
                            if subject:
                                subject = subject[0]

                            lang_exists = Subject_Language.objects.filter(subject=subject, language=selected_language)

                            lang_level = Language_Level.objects.filter(language_level_id=request.POST['language_fluency_' + str(response_languages[i])])
                            if lang_level:
                                lang_level = lang_level[0]

                            if not lang_exists:
                                Subject_Language.objects.create(subject=subject, language=selected_language, level=lang_level)
                            else:
                                Subject_Language.objects.filter(subject=subject, language=selected_language).update(level=lang_level)

                    if 'language_other' in request.POST:
                        response_languages = request.POST.getlist('language_other')
                        for i in range(len(response_languages)):

                            sel_response_language = response_languages[i]
                            if sel_response_language:
                                selected_language = Language.objects.get(language_id=sel_response_language)
                                subject = Subject.objects.filter(user_id=request.user.id)
                                if subject:
                                    subject = subject[0]

                                lang_exists = Subject_Language.objects.filter(subject=subject, language=selected_language)

                                lang_level = None
                                lang_level = Language_Level.objects.filter(language_level_id=request.POST['other_fluency_' + str(i+1)])
                                if lang_level:
                                    lang_level = lang_level[0]

                                if not lang_exists:
                                    Subject_Language.objects.create(subject=subject, language=selected_language, level=lang_level)
                                else:
                                    Subject_Language.objects.filter(subject=subject, language=selected_language).update(level=lang_level)


                    # Education level
                    response_education_level = request.POST['education_level']
                    selected_education_level = Education_Level.objects.filter(education_level_id=response_education_level)
                    if selected_education_level:
                        selected_education_level = selected_education_level[0]
                        Subject.objects.filter(user_id=request.user.id).update(education_level=selected_education_level)

                    # Dementia type
                    if 'dementia_type' in request.POST:
                        response_dementia_type = request.POST.getlist('dementia_type')
                        for i in range(len(response_dementia_type)):
                            selected_dementia_type = Dementia_Type.objects.filter(dementia_type_id=response_dementia_type[i])
                            selected_dementia_name = ""
                            if selected_dementia_type:
                                selected_dementia_type = selected_dementia_type[0]
                                if selected_dementia_type.requires_detail:
                                    if 'dementia_type_detail_' + str(response_dementia_type[i]) in request.POST:
                                        selected_dementia_name = request.POST['dementia_type_detail_' + str(response_dementia_type[i])]

                            subject = Subject.objects.filter(user_id=request.user.id)
                            if subject:
                                subject = subject[0]

                            dementia_type_exists = Subject_Dementia_Type.objects.filter(subject=subject, dementia_type_id=selected_dementia_type.dementia_type_id)
                            if not dementia_type_exists:
                                Subject_Dementia_Type.objects.create(subject=subject, dementia_type_id=selected_dementia_type.dementia_type_id, dementia_type_name=selected_dementia_name)

                    # Dementia meds
                    response_dementia_med = request.POST['dementia_med']
                    map_response_to_id = { 'yes': 1, 'no': 0}
                    if response_dementia_med in map_response_to_id:
                        response_dementia_med_id = map_response_to_id[response_dementia_med]
                        Subject.objects.filter(user_id=request.user.id).update(dementia_med=response_dementia_med_id)

                    # Smoking
                    response_smoking = request.POST['smoking']
                    map_response_to_id = { 'yes': 1, 'no': 0}
                    if response_smoking in map_response_to_id:
                        response_smoking_id = map_response_to_id[response_smoking]
                        Subject.objects.filter(user_id=request.user.id).update(smoker_recent=response_smoking_id)

                    # Country of origin
                    Subject.objects.filter(user_id=request.user.id).update(origin_country=response_country_origin)

                    # Country of residence
                    Subject.objects.filter(user_id=request.user.id).update(residence_country=response_country_res)

                    # Set the demographic flag to 1
                    Subject.objects.filter(user_id=request.user.id).update(date_demographics_submitted=date_submitted)
        subject = Subject.objects.get(user_id=request.user.id)

        if subject:
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted

            # Demographic survey options/dropdowns
            if not demographic_submitted:
                gender_options = Gender.objects.all().order_by('ranking')
                language_options = Language.objects.all().exclude(is_official=0).order_by('name')
                language_other = Language.objects.all().exclude(is_official=1).order_by('name')
                language_fluency_options = Language_Level.objects.all().order_by('ranking')
                ethnicity_options = Ethnicity.objects.all().order_by('ranking')
                education_options = Education_Level.objects.all().order_by('-ranking')
                dementia_options = Dementia_Type.objects.all().order_by('ranking')
                country_res_options = Country.objects.all().order_by('name')

            # Check if the user is associated with any active bundles
            subject_bundle = Subject_Bundle.objects\
                             .filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), \
                                     subject=subject, \
                                     active_startdate__lte=today)
            if subject_bundle:
                subject_bundle = subject_bundle[0]
                if subject_bundle.bundle.bundle_id in [WCH_PHONE_BUNDLE.bundle_id, WCH_WEB_BUNDLE.bundle_id]:
                    is_wch_user = True
            completed_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=False).order_by('start_date')
            active_sessions = active_sessions = Session.objects\
                                                       .filter(start_date__lte=cutoff_date, \
                                                               subject__user_id=request.user.id, \
                                                               end_date__isnull=True)\
                                                       .order_by('start_date')
            pending_sessions = Session.objects\
                                      .filter(start_date__gt=cutoff_date, \
                                              subject__user_id=request.user.id, \
                                              end_date__isnull=True, \
                                              session_type__name='website')\
                                      .order_by('start_date')

            num_completed_sessions = len(completed_sessions)
            num_active_sessions = len(active_sessions)
            num_pending_sessions = len(pending_sessions)

            percentage_completed = []
            for i, session in enumerate(active_sessions):
                num_current_task = Session_Task.objects\
                                               .filter(session=session, \
                                                       date_completed__isnull=False)\
                                               .count()
                num_tasks = Session_Task.objects.filter(session=session).count()
                percentage_completed.append(min(100, round(num_current_task*100.0/num_tasks)))

            completed_sessions = zip(completed_sessions, range(1, num_completed_sessions + 1))
            active_sessions = zip(active_sessions, percentage_completed, range(num_completed_sessions + 1, num_completed_sessions + num_active_sessions + 1))
            pending_sessions = zip(pending_sessions, range(num_completed_sessions + num_active_sessions + 1, num_pending_sessions + num_active_sessions + num_completed_sessions + 1))

    dict_language = {}
    dict_language_other = {}

    form_languages = [int(sel_lang) for sel_lang in request.POST.getlist('language') ]
    form_languages_other = [int(sel_lang) for sel_lang in request.POST.getlist('language_other') if sel_lang ]

    for i in range(len(form_languages)):
        if i < len(form_languages_fluency) and i >= 0:
            dict_language[form_languages[i]] = form_languages_fluency[i]
        else:
            dict_language[form_languages[i]] = ""

    for i in range(len(form_languages_other)):
        if i < len(form_languages_other_fluency) and i >= 0:
            dict_language_other[form_languages_other[i]] = form_languages_other_fluency[i]
        else:
            dict_language_other[form_languages_other[i]] = ""

    passed_vars = {
        'is_wch_user': is_wch_user,
        'is_authenticated': is_authenticated,
        'consent_submitted': consent_submitted,
        'demographic_submitted': demographic_submitted,
        'completed_sessions': completed_sessions,
        'active_sessions': active_sessions,
        'pending_sessions': pending_sessions,
        'subject_bundle': subject_bundle,
        'dict_language': dict_language,
        'dict_language_other': dict_language_other,
        'form_values': request.POST,
        'form_languages_other_fluency': form_languages_other_fluency,
        'form_ethnicity': [int(sel_eth) for sel_eth in request.POST.getlist('ethnicity')],
        'form_errors': form_errors,
        'gender_options': gender_options,
                   'language_options': language_options, 'language_other': language_other,
                   'language_fluency_options': language_fluency_options, 'ethnicity_options': ethnicity_options,
                   'education_options': education_options, 'dementia_options': dementia_options,
                   'country_res_options': country_res_options,
    }
    passed_vars.update(global_passed_vars)

    return render_to_response('datacollector/wch/main.html', passed_vars, context_instance=RequestContext(request))


def session(request, session_id):
    '''
        Display session view.
    '''

    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    active_notifications = []
    is_wch_study = False

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

        # Check if WCH study
        today = datetime.datetime.now().date()
        subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)
        if subject_bundle:
            subject_bundle = subject_bundle[0]
            if subject_bundle.bundle.name_id == 'wch_web' or subject_bundle.bundle.name_id == 'wch_phone':
                is_wch_study = True

        session = Session.objects.filter(session_id=session_id)
        if session:
            session = session[0]

            # Initialize global vars for session page
            requires_audio = False
            existing_responses = False
            num_current_task = Session_Task.objects.filter(session=session,date_completed__isnull=False).count() + 1
            num_tasks = Session_Task.objects.filter(session=session).count()
            session_summary = ""
            active_task = None
            active_session_task_id = None
            active_instances = None
            next_session_date = None

            if not session.end_date:
                if request.method == 'POST':
                    ## Submit response
                    json_data = submit_response(request, session)
                    return HttpResponse(json.dumps(json_data), content_type="application/json")

                # Update the date_last_session_access for the user (this drives reminder emails)
                date_access = datetime.datetime.now()
                Subject.objects.filter(user_id=request.user.id).update(date_last_session_access=date_access)

                # If the session is active, find the first unanswered task instance to display
                active_task = None
                active_instances = []
                active_session_task_id = None
                display_thankyou = False

                # Get next session
                next_sessions = Session.objects.filter(subject_id=subject.user_id, end_date__isnull=True).order_by('start_date')
                if next_sessions:
                    next_session_date = next_sessions[0].start_date

                # Get active task
                active_task = get_active_task(session)

                if active_task:
                    active_session_task_id = active_task.session_task_id
                    active_task_instance_values = get_active_task_instances(session, active_task)

                    if active_task.task.name_id in ['picture_description', 'rig', 'story_recall']:
                        requires_audio = True

                    for instance_value in active_task_instance_values:

                        # Determine how to display the value based on the field type
                        active_instances += [get_display(active_task.task, instance_value)]
                else:
                    # If no active task, session is complete.
                    Session.objects.filter(session_id=session.session_id).update(end_date=today)

                    # Refresh
                    return HttpResponseRedirect(WCH_WEBSITE_ROOT + 'session/' + str(session.session_id))

            else:
                display_thankyou = True
                summary_tasks = Session_Task.objects.filter(session=session).order_by('order')
                counter = 1
                for next_task in summary_tasks:
                    next_task_instances = Session_Task_Instance.objects\
                                                               .filter(session_task=next_task)\
                                                               .aggregate(count_instances=Count('session_task_instance_id'))
                    session_summary += "<tr><td>" + str(counter) + "</td><td>" + next_task.task.name + "</td><td>" + str(next_task_instances['count_instances']) + "</td></tr>"
                    counter += 1
            passed_vars = {
                'session': session,
                'is_authenticated': is_authenticated,
                'consent_submitted': consent_submitted,
                'demographic_submitted': demographic_submitted,
                'active_notifications': active_notifications,
                'is_wch_study': is_wch_study,
                'percentage_completion': min(100, round(num_current_task*100.0/num_tasks)),
                'active_task': active_task,
                'active_session_task_id': active_session_task_id,
                'active_instances': active_instances,
                'requires_audio': requires_audio,
                'completed_date': session.end_date,
                'display_thankyou': display_thankyou,
                'session_summary': session_summary,
                'next_session_date': next_session_date
            }
            passed_vars.update(global_passed_vars)

            return render_to_response('datacollector/wch/session.html', passed_vars, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(WCH_WEBSITE_ROOT)

def about(request):
    """
    WCH about page.
        :param request:
    """
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
    return render_to_response('datacollector/wch/about.html', passed_vars, context_instance=RequestContext(request))

def login(request):

    # If there is a currently logged in user, just redirect to home page
    if request.user.is_authenticated():

        # Check if the user is associated with any active bundles
        subject = Subject.objects.get(user_id=request.user.id)
        today = datetime.datetime.now().date()
        subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)
        if subject_bundle:
            if subject_bundle[0].bundle.name_id == 'wch_web' or subject_bundle[0].bundle.name_id == 'wch_phone':
                return HttpResponseRedirect(WCH_WEBSITE_ROOT)

        return HttpResponseRedirect(WCH_WEBSITE_ROOT)

    # If the form has been submitted, validate the data and
    errors = []
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    auth_login(request, user)

                    # Check if the user is associated with any active bundles
                    subject = Subject.objects.get(user_id=user.id)
                    today = datetime.datetime.now().date()
                    subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)
                    if subject_bundle:
                        if subject_bundle[0].bundle.name_id == 'wch_web' or subject_bundle[0].bundle.name_id == 'wch_phone':
                            return HttpResponseRedirect(WCH_WEBSITE_ROOT)

                    # Success: redirect to the home page
                    return HttpResponseRedirect(WCH_WEBSITE_ROOT)
                else:
                    # Return a 'disabled account' error message
                    errors.append("Your account is currently disabled. Please contact the website administrator for assistance.")
            else:
                # Return an 'invalid login' error message
                errors.append("Invalid login credentials, please try again.")
    else:
        form = LoginForm()

    passed_vars = {'form': form, 'errors': errors}
    passed_vars.update(global_passed_vars)
    return render_to_response('datacollector/wch/login.html', passed_vars, context_instance=RequestContext(request))