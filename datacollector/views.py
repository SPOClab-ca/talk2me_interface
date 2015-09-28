# Create your views here.

from django import forms
from django.db.models import Q, Count
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from datacollector.forms import *
from datacollector.models import *
from csc2518.settings import STATIC_URL
from csc2518.settings import SUBSITE_ID

import datetime
import json
import random
import re

import crypto
import emails
import notify

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

colour_lookup = {'red': 'ff0000', 'green': '00ff00', 'blue': '0000ff', 'brown': '6f370f', 'purple': '7c26cb'}

date_format = "%Y-%m-%d"
age_limit = 18
regex_email = re.compile(r"[^@]+@[^@]+\.[^@]+")
regex_date = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")

    
# Common lib functions ------------------------------------------------------
def generate_session(subject, session_type):
    
    # If the user has any active task bundles, then generate the tasks from the bundles only. 
    # The active date range for the bundle is inclusive.
    today = datetime.datetime.now().date()
    active_bundles = Subject_Bundle.objects.filter( Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today )
    if active_bundles:
        active_tasks = []
        for subj_bundle in active_bundles:
            active_tasks += [x.task for x in subj_bundle.bundle.bundle_task_set.all()]
    # Otherwise, generate all active tasks.
    else:
        active_tasks = Task.objects.filter(is_active=1)
        if session_type.text_only:
            active_tasks = Task.objects.filter(is_active=1, instruction_phone__isnull=False)
        
    active_task_ids = [t.task_id for t in active_tasks]
    
    # Randomly shuffle the order of the tasks in the session, except for the tasks with fixed order (e.g., disposition task)
    active_task_order = [(t.default_order, t.is_order_fixed) for t in active_tasks]
    idx_to_shuffle = [i for i, x in enumerate(active_task_order) if x[1] == 0]
    tasks_to_shuffle = [active_task_order[i] for i in idx_to_shuffle]
    random.shuffle(tasks_to_shuffle)
    for i in range(len(idx_to_shuffle)):
        active_task_order[idx_to_shuffle[i]] = tasks_to_shuffle[i]
    
    startdate = datetime.datetime.now()
    new_session = Session.objects.create(subject=subject, start_date=startdate, end_date=None, session_type=session_type)
    
    # Select random task questions for the session  
    counter_task = 0
    for task_id in active_task_ids:
        task = Task.objects.get(task_id=task_id)
        num_instances = task.default_num_instances
        task_order = task.default_order
        shuffled_order = active_task_order[counter_task][0]
        task_delay = task.default_delay
        task_embedded_delay = task.default_embedded_delay
        
        # Add the task to the current session in the database
        new_task = Session_Task.objects.create(session=new_session, task=task, order=shuffled_order, delay=task_delay, embedded_delay=task_embedded_delay)

        # Update the database to reflect <num_instances> instances of this task for this session
        new_task_instances = []
        for num in range(num_instances):
            new_task_instance = Session_Task_Instance.objects.create(session_task=new_task)
            # Add a response entry for each task instance
            new_task_instance_response = Session_Response.objects.create(session_task_instance=new_task_instance)
            
            new_task_instances += [new_task_instance]

        # Select random field values for each of the new task instances 
        # (only for the fields that need to have generated values, i.e. for display fields)
        task_fields_display = Task_Field.objects.filter(task=task,field_type__name='display',generate_value=1)
        
        # For each display field, select random <num_instances> which the user hasn't seen before
        for field in task_fields_display:
            
            existing_instances = Session_Task_Instance_Value.objects.filter(task_field=field, session_task_instance__session_task__session__subject=subject)
            existing_values = [v.value for v in existing_instances]
            
            # Add to selected values. Make sure not to add field values that are associated with each other, or are already selected, or have been seen by the subject before in previous sessions. NB: here we are assuming that the total number of values for each field in the db is at least as big as the default number of instances for the field.
            selected_values = []
            limits = []
            while len(selected_values) < num_instances:
                
                field_values = Task_Field_Value.objects.filter(task_field=field,*limits).exclude(value__in=existing_values)
                if field_values:
                    selected_values += [random.choice(field_values)]
                else:
                    # If there aren't any results, relax the query by restricting only to values that haven't been seen before
                    field_values = Task_Field_Value.objects.filter(task_field=field).exclude(value__in=existing_values)
                    if field_values:
                        selected_values += [random.choice(field_values)]
                    else:
                        # If there aren't any results (i.e., the subject has seen all possible values for this field), then relax the query by just selecting values that are different from the currently selected values (i.e., don't want any repeating values in the current session if possible, which should be the case as long as the number of values for the field is greater than the default number of instances for the field).
                        field_values = Task_Field_Value.objects.filter(task_field=field,*limits)
                        if field_values:
                            selected_values += [random.choice(field_values)]
                        else:
                            # If there still aren't any results (i.e., the subject has seen all possible values for this field), relax the query completely by selecting any random field value, regardless of whether the subject has seen it before or whether it has been selected for the current session (i.e., allow repeats).
                            field_values = Task_Field_Value.objects.filter(task_field=field)
                            if field_values:
                                selected_values += [random.choice(field_values)]
                            else:
                                # The database doesn't contain any entries for this task field.
                                # Fail, display an error page.
                                return HttpResponseRedirect(website_root + 'error/501')
                
                # Build limit query with Q objects: enforce no repetition of the same item in the same task instance,
                # and no selection of mutually associated items in the same task instance.
                selected_assoc_ids = [item.assoc_id for item in selected_values]
                selected_ids = [item.task_field_value_id for item in selected_values]
                limit_assoc = [~Q(task_field_value_id=i) for i in selected_assoc_ids if i]
                limit_id = [~Q(task_field_value_id=i) for i in selected_ids if i]
                limits = limit_assoc + limit_id
                
                # Special case: Stroop task. Enforce the special restriction that consecutive items are not of 
                # the same ink colour, and do not spell out the same colour word.
                if task.name_id == "stroop" and selected_values:
                    limits += [ ~Q(response_expected = selected_values[-1].response_expected), \
                                ~Q(value_display = selected_values[-1].value_display) ]
                
            
            for index_instance in range(num_instances):
                instance_value = selected_values[index_instance]
                new_session_value = Session_Task_Instance_Value.objects.create(session_task_instance=new_task_instances[index_instance], task_field=field, value=instance_value.value, value_display=instance_value.value_display, difficulty=instance_value.difficulty)
                
                # Using the task field value ("instance_value"), update the expected session response
                Session_Response.objects.filter(session_task_instance=new_task_instances[index_instance]).update(value_expected=instance_value.response_expected)

                # If there are any associated fields (e.g., answer field instances associated with the currently selected question field instances), add them to the session as well.
                # Note that for select options, all options must be added, not just the one that is the correct response.
                linked_field_instances = list(Task_Field_Value.objects.filter(Q(assoc=instance_value) | Q(assoc=instance_value.assoc)).exclude(task_field=field).exclude(assoc__isnull=True))
                
                # Scramble the order of the linked instances randomly, so the subject won't know the order of the correct options.
                random.shuffle(linked_field_instances)
                
                for linked_instance in linked_field_instances:
                    score = 0
                    if linked_instance.assoc.task_field_value_id == instance_value.task_field_value_id:
                        score = 1
                    
                    new_session_value = Session_Task_Instance_Value.objects.create(session_task_instance=new_task_instances[index_instance], task_field=linked_instance.task_field, value=linked_instance.value, value_display=linked_instance.value_display, difficulty=linked_instance.difficulty)
        counter_task += 1
        
    return new_session  

# END of common lib functions ------------------------------------------------------    
  
  
def index(request):
    
    # Authenticate current user. If no user logged in, redirect to login page.
    is_authenticated = False
    completed_sessions = []
    active_sessions = []
    active_notifications = []
    consent_submitted = False
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
    subject_bundle = None
    bundle_id = None
    bundle_token = None
    if 'bid' in request.GET and 'bt' in request.GET:
        bundle_id = request.GET['bid']
        bundle_token = request.GET['bt']
    
    if request.user.is_authenticated():
        is_authenticated = True

        if request.method == 'POST':
            date_submitted = datetime.datetime.now()
            form_type = request.POST['form_type']
            if form_type == 'consent':
                
                # Perform form validation first
                # - check that consent has been provided
                if 'radio_consent' not in request.POST:
                    form_errors += ['You did not provide consent by selecting the appropriate option. If you do not consent to this form, you cannot use ' + str(global_passed_vars['website_name']) + "." ]
                
                # - check that if any of the email-related options has been selected, the email address is provided
                user_email = ""
                if 'email_address' in request.POST:
                    user_email = request.POST['email_address']
                    
                    if user_email:
                        # Validate user email if provided
                        if not regex_email.match(user_email):
                            form_errors += ['The e-mail address you provided does not appear to be valid.']
                    
                # Dictionary of options which require a user email
                options_req_email = {'cb_preference_email_reminders': 'scheduled e-mail reminders', 
                                     'cb_preference_email_updates': 'electronic communication regarding study outcomes',
                                     'cb_preference_prizes': 'monthly prize draws'}
                options_selected = set(options_req_email.keys()).intersection(set(request.POST.keys()))
                if options_selected and not user_email:
                    connector = " || "
                    plur_s = ""
                    if len(options_selected) > 1: plur_s = "s"
                    options_selected_str = connector.join([options_req_email[opt] for opt in options_selected])
                    num_conn = options_selected_str.count(connector)
                    options_selected_str = options_selected_str.replace(connector, ", ", num_conn-1)
                    options_selected_str = options_selected_str.replace(connector, ", and ")
                        
                    form_errors += ['You did not provide an e-mail address. An e-mail address is required since you selected the following option' + plur_s + ': ' + options_selected_str + "."]
                    
                # - check that an email reminder frequency is specified, if reminders are requested
                if 'cb_preference_email_reminders' in request.POST and 'radio_email_reminders_freq' not in request.POST:
                    form_errors += ['You have not selected a frequency for the scheduled e-mail reminders.']
                    
                    
                if not form_errors:
                    
                    # Record user email, if provided, and send a verification email
                    if user_email:
                        new_email_token = crypto.generate_confirmation_token(request.user.username + user_email)
                        confirmation_link = website_hostname + "/activate/" + new_email_token  
                        
                        emailText = "Welcome to " + global_passed_vars['website_name'] + "!\n\nThank you for registering an account.\n\nPlease click this link to confirm your email address:\n\n<a href=\"" + confirmation_link + "\">" + confirmation_link + "</a>\n\nIf the link above does not work, please copy and paste it into your browser's address bar.\n\nWhy am I verifying my email address? We value your privacy and want to make sure that you are the one who initiated this registration. If you received this email by mistake, you can make it all go away by simply ignoring it."
                        
                        emailHtml = """<h2 style="Margin-top: 0;color: #44a8c7;font-weight: 700;font-size: 24px;Margin-bottom: 16px;font-family: Lato,sans-serif;line-height: 32px;text-align: center">Welcome to """ + global_passed_vars['website_name'] + """!</h2>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">Thank you for registering an account.</p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><strong>Please click this link to confirm your email address:</strong></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><u><a href=\"""" + confirmation_link + """\">""" + confirmation_link + """</a></u></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">If the link above does not work, please copy and paste it into your browser's address bar.</p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><strong>Why am I verifying my email address?</strong>\r\n We value your privacy and want to make sure that you are the one who initiated this registration. If you received this email by mistake, you can make it all go away by simply ignoring it.</p>\r\n"""
                        
                        successFlag = emails.sendEmail(email_username, email_name, [user_email], [], [], global_passed_vars['website_name'] + " - Email Confirmation", emailText, emails.emailPre + emailHtml + emails.emailPost)
                        
                        # Update database to keep a record of sent emails, if the mailer was successful
                        if successFlag:
                            s = Subject.objects.get(user_id=request.user.id)
                            Subject_Emails.objects.create(date_sent=datetime.datetime.now().date(), subject=s, email_from=email_username, email_to=user_email, email_type='email_confirmation')
                        
                        User.objects.filter(id=request.user.id).update(email=user_email)
                        Subject.objects.filter(user_id=request.user.id).update(email_validated=0,email_token=new_email_token)
                    
                    # Update consent details
                    Subject.objects.filter(user_id=request.user.id).update(date_consent_submitted=date_submitted)
                    if request.POST['radio_consent'] == 'alternate':
                        Subject.objects.filter(user_id=request.user.id).update(consent_alternate=1)
                    
                    # Preference for allowing public release of collected data
                    if 'cb_preference_public_release' in request.POST:
                        Subject.objects.filter(user_id=request.user.id).update(preference_public_release=1)
                        
                    # Preference for receiving email reminders about completing sessions
                    if 'cb_preference_email_reminders' in request.POST:
                        reminders_freq = request.POST['radio_email_reminders_freq']
                        Subject.objects.filter(user_id=request.user.id).update(preference_email_reminders=1,preference_email_reminders_freq=reminders_freq,email_reminders=user_email)
                    
                    # Preference for receiving email updates about related future research/publications
                    if 'cb_preference_email_updates' in request.POST:
                        Subject.objects.filter(user_id=request.user.id).update(preference_email_updates=1,email_updates=user_email)
                    
                    # Preference for participation in monthly prize draws
                    if 'cb_preference_prizes' in request.POST:
                        Subject.objects.filter(user_id=request.user.id).update(preference_prizes=1,email_prizes=user_email)
            
            elif form_type == 'demographic':
            
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
                
        # Assume that every authenticated user exists in subject. If they don't, add them with the appropriate ID, and all flags initialized to null/false.
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
        else:
            date_submitted = datetime.datetime.now()
            subject = Subject.objects.create(user_id=request.user.id, date_created=date_submitted, consent_alternate=0, email_validated=0, preference_email_reminders=0, preference_email_updates=0, preference_public_release=0, preference_prizes=0)
        
        # If first time logging in, display Consent Form, and ask for consent
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
        
        # For the currently logged on user who has completed both consent and demographic forms, populate the index/dashboard
        # page with their previously completed and active sessions, and any notifications
        if consent_submitted and demographic_submitted:
            completed_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=False).order_by('-start_date')
            active_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=True).order_by('-start_date')
            
            # Fetch all notifications that are active and have not been dismissed by the user 
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = notify.get_active_new(subject)
            
            # Check if the user is associated with any active bundles
            today = datetime.datetime.now().date()
            subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)
            if subject_bundle:
                subject_bundle = subject_bundle[0]
            else:    
                # If the URL contains a bundle association, then create it if it doesn't already exist.
                # A user is assumed to be a part of one bundle at a time only.
                # Validate the passed in bundle parameters:
                bundle_exists = False
                bundle_valid = False
                if bundle_id and bundle_token and bundle_id.isdigit():
                    bundle_exists = Bundle.objects.filter(bundle_id=bundle_id)
                    if bundle_exists:
                        bundle_exists = bundle_exists[0]    
                        if bundle_exists.bundle_token == bundle_token:
                            bundle_valid = True
                        
                # If the passed in bundle parameter is valid, then assign the logged in user
                # on this page to the relevant task bundle, if they are not already assigned
                if bundle_exists and bundle_valid:
                    subj_bundle_token = crypto.generate_confirmation_token(str(subject.user_id) + str(bundle_exists.bundle_id) + str(bundle_exists.completion_req_sessions))
                    new_subject_bundle = Subject_Bundle.objects.create(subject=subject, bundle=bundle_exists, active_startdate=today, active_enddate=bundle_exists.active_enddate, completion_token=subj_bundle_token, completion_req_sessions=bundle_exists.completion_req_sessions)
                
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
    
    # , 'form_languages': form_languages, 'form_languages_other': form_languages_other, 'form_languages_fluency': form_languages_fluency
    passed_vars = {'is_authenticated': is_authenticated, 'dict_language': dict_language, 'dict_language_other': dict_language_other, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'form_values': request.POST, 'form_languages_other_fluency': form_languages_other_fluency, 'form_ethnicity': [int(sel_eth) for sel_eth in request.POST.getlist('ethnicity')], 'form_errors': form_errors, 'completed_sessions': completed_sessions, 'active_sessions': active_sessions, 'active_notifications': active_notifications, 'user': request.user, 'gender_options': gender_options, 'language_options': language_options, 'language_other': language_other, 'language_fluency_options': language_fluency_options, 'ethnicity_options': ethnicity_options, 'education_options': education_options, 'dementia_options': dementia_options, 'country_res_options': country_res_options, 'subject_bundle': subject_bundle }
    passed_vars.update(global_passed_vars)
    return render_to_response('datacollector/index.html', passed_vars, context_instance=RequestContext(request))

def login(request):

    # If there is a currently logged in user, just redirect to home page
    if request.user.is_authenticated():
        return HttpResponseRedirect(website_root)
    
    # If the form has been submitted, validate the data and 
    errors = []    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    auth_login(request,user)
                    # Success: redirect to the home page
                    return HttpResponseRedirect(website_root)
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
    
    return render_to_response('datacollector/login.html', passed_vars, context_instance=RequestContext(request))


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(website_root)


def register(request):

    bundle_id = None
    bundle_token = None
    get_querystring = ""
    if 'bid' in request.GET and 'bt' in request.GET:
        bundle_id = request.GET['bid']
        bundle_token = request.GET['bt']
        get_querystring = "?bid=" + bundle_id + "&bt=" + bundle_token
        
    # If there is a currently logged in user, just redirect to home page
    if request.user.is_authenticated():
        return HttpResponseRedirect(website_root + get_querystring)
    
    # If the form has been submitted, validate the data and login the user automatically
    errors = []
    today = datetime.datetime.now().date()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_user = form.save()
            
            # Create a corresponding subject in the app
            new_subject = Subject.objects.create(user_id=new_user.id, date_created=datetime.datetime.now())
            
            # Validate the passed in bundle parameters
            bundle_exists = False
            bundle_valid = False
            if 'bundle_id' in request.POST and 'bundle_token' in request.POST:
                bundle_id = request.POST['bundle_id']
                bundle_token = request.POST['bundle_token']
                if bundle_id and bundle_token and bundle_id.isdigit():
                    bundle_exists = Bundle.objects.filter(bundle_id=bundle_id)
                    if bundle_exists:
                        bundle_exists = bundle_exists[0]    
                        if bundle_exists.bundle_token == bundle_token:
                            bundle_valid = True
                    
            # If the passed in bundle parameter is valid, then assign the newly created user
            # on this page to the relevant task bundle
            if bundle_exists and bundle_valid:
                subj_bundle_token = crypto.generate_confirmation_token(str(new_subject.user_id) + str(bundle_exists.bundle_id) + str(bundle_exists.completion_req_sessions))
                new_subject_bundle = Subject_Bundle.objects.create(subject=new_subject, bundle=bundle_exists, active_startdate=today, active_enddate=bundle_exists.active_enddate, completion_token=subj_bundle_token, completion_req_sessions=bundle_exists.completion_req_sessions)
            
            # Automatically log the user in and redirect to index page
            new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            auth_login(request,new_user)
            
            return HttpResponseRedirect(website_root)
    else:
        form = UserCreationForm()

    passed_vars = {'form': form, 'bundle_id': bundle_id, 'bundle_token': bundle_token}
    passed_vars.update(global_passed_vars)
    
    return render_to_response('datacollector/register.html', passed_vars, context_instance=RequestContext(request))

def question(request, session_id, instance_id):
    passed_vars = {'session': session, 'subject': subject, 'task_instance': instance}
    passed_vars.update(global_passed_vars)
    return render_to_response('datacollector/question.html', passed_vars)


def startsession(request):
    # Begin a new session for the current user: set up the database tables, 
    # the task instances and the response fields.
    
    if request.user.is_authenticated():
        
        subject = Subject.objects.get(user_id=request.user.id)
        session_type = Session_Type.objects.get(name='website')
        new_session = generate_session(subject, session_type)         
        return HttpResponseRedirect(website_root + 'session/' + str(new_session.session_id))
    else:
        return HttpResponseRedirect(website_root)

def notfound(request):
    
    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    
    if request.user.is_authenticated():
        is_authenticated = True
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted
            
    passed_vars = {'user': request.user, 'is_authenticated': is_authenticated, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted}
    passed_vars.update(global_passed_vars)
    
    return render_to_response('datacollector/notfound.html', passed_vars, context_instance=RequestContext(request))
    
def activate(request, user_token):

    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    email_prevalidated = False
    email_validated = False
    email_address = ""
    active_notifications = []
    
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
            
    # Determine if the token is valid
    s = Subject.objects.filter(email_token=user_token)
    if not s:
        return HttpResponseRedirect(website_root + "404")
    
    # Determine if user's email is already confirmed
    u = User.objects.filter(id=s[0].user_id)
    if u:
        email_address = u[0].email
        if s[0].email_validated:
            email_prevalidated = True
        else:
            s.update(email_validated=1)
            email_validated = True
        
    passed_vars = {'user': request.user, 'is_authenticated': is_authenticated, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications, 'email_prevalidated': email_prevalidated, 'email_validated': email_validated, 'email_address': email_address}
    passed_vars.update(global_passed_vars)
    
    return render_to_response('datacollector/activate.html', passed_vars, context_instance=RequestContext(request))
    

def session(request, session_id):

    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    active_notifications = []
    
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
            
        session = Session.objects.filter(session_id=session_id)
        if session:
            session = session[0]

            # Update the date_last_session_access for the user (this drives reminder emails)
            date_access = datetime.datetime.now()
            Subject.objects.filter(user_id=request.user.id).update(date_last_session_access=date_access)
            
            # If the session is active, find the first unanswered task instance to display
            active_task = None
            active_instances = []   
            serial_instances = False
            serial_startslide = ""
            active_session_task_id = None
            display_thankyou = False
            
            # Initialize global vars for session page
            requires_audio = False
            existing_responses = False
            num_current_task = Session_Task.objects.filter(session=session,date_completed__isnull=False).count() + 1
            num_tasks = Session_Task.objects.filter(session=session).count()
            completed_date = session.end_date
            session_summary = ""
            
            if not session.end_date:
                
                # If session responses are submitted, perform validation. If validation passes, write them to the database and return a 'success' response to the AJAX script. If validation fails, return a 'fail' response to the AJAX script, along with the form errors found.
                if request.method == "POST":
                    
                    form_errors = []
                    json_data = {}
                    json_data['status'] = 'fail'
                    
                    active_task = Session_Task.objects.filter(session=session,date_completed__isnull=True).order_by('order')
                    if active_task:
                        active_task = active_task[0].task
                        
                        # Validate the form first
                        if 'response' in request.POST and 'instanceid' in request.POST:
                            responses = request.POST.getlist('response')
                            instances = request.POST.getlist('instanceid')
                            for i in range(len(responses)):
                                response = responses[i]
                                next_instance = instances[i]
                                if not response:
                                    form_errors += ['You did not provide a response for question #' + str(i+1) + '.']
                                if not next_instance:
                                    form_errors += ['Question #' + str(i+1) + ' is invalid.']
                                else:
                                    instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)
                                    if not instance:
                                        form_errors += ['Question #' + str(i+1) + ' is invalid.']
                        
                        elif 'instanceid' in request.POST:
                            instances = request.POST.getlist('instanceid')
                            for i in range(len(instances)):
                                # The audio questions are already transmitted to db, ignore those
                                audio_label = 'response_audio_' + str(instances[i])
                                if not audio_label in request.POST:
                                    response_label = 'response_' + str(instances[i])
                                    if response_label in request.POST:
                                        response = request.POST[response_label]
                                        next_instance = instances[i]
                                        if not response:
                                            form_errors += ['You did not provide a response for question #' + str(i+1) + '.']
                                        if not next_instance:
                                            form_errors += ['Question #' + str(i+1) + ' is invalid.']
                                        else:
                                            instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)
                                            if not instance:
                                                form_errors += ['Question #' + str(i+1) + ' is invalid.']
                                    else:
                                        form_errors += ['You did not provide a response for question #' + str(i+1) + '.']
                            
                        # Process any input, textarea (text), and multiselect responses
                        if not form_errors:
                            if 'response' in request.POST and 'instanceid' in request.POST:
                                responses = request.POST.getlist('response')
                                instances = request.POST.getlist('instanceid')
                                for i in range(len(responses)):
                                    response = responses[i]
                                    instance = Session_Task_Instance.objects.filter(session_task_instance_id=instances[i])[0]
                                    
                                    # Find the response field type for this task
                                    response_data_type = Task_Field.objects.filter(task=instance.session_task.task,field_type__name='input')[0].field_data_type
                                    
                                    # Update the appropriate entry in the database (NB: 'audio' responses are not handled here; they are saved to database as soon as they are recorded, to avoid loss of data)                         
                                    if response_data_type == 'multiselect':
                                        Session_Response.objects.filter(session_task_instance=instance).update(value_multiselect=response,date_completed=datetime.datetime.now())
                                    else:
                                        Session_Response.objects.filter(session_task_instance=instance).update(value_text=response,date_completed=datetime.datetime.now())
                                        
                            # Process any radio selection responses (different ID for the radio group for each instance of the task)
                            if 'instanceid' in request.POST:
                                instances = request.POST.getlist('instanceid')
                                for i in range(len(instances)):
                                    audio_label = 'response_audio_' + str(instances[i])
                                    if not audio_label in request.POST:
                                        response_label = 'response_' + str(instances[i])
                                        if response_label in request.POST:
                                            response = request.POST[response_label]
                                            instance = Session_Task_Instance.objects.filter(session_task_instance_id=instances[i])[0]
                                            
                                            # Find the response field type for this task
                                            response_data_type = Task_Field.objects.filter(task=instance.session_task.task,field_type__name='input')[0].field_data_type
                                            
                                            if response_data_type == 'select':
                                                Session_Response.objects.filter(session_task_instance=instance).update(value_text=response,date_completed=datetime.datetime.now())
                                            else:
                                                Session_Response.objects.filter(session_task_instance=instance).update(value_text=response,date_completed=datetime.datetime.now())
                            
                            # Mark the task as submitted
                            Session_Task.objects.filter(session=session,task=active_task).update(date_completed=datetime.datetime.now())
                            
                            json_data['status'] = 'success'
                        
                    if form_errors:
                        json_data['error'] = [dict(msg=x) for x in form_errors]
                    return HttpResponse(json.dumps(json_data))
                
                num_current_task = Session_Task.objects.filter(session=session,date_completed__isnull=False).count() + 1
                num_tasks = Session_Task.objects.filter(session=session).count()  
                active_task = Session_Task.objects.filter(session=session,date_completed__isnull=True).order_by('order')
                if not active_task:
                    # All tasks in the current session have been completed - mark the session as complete with an end date stamp, and display acknowledgement. Display summary. Trigger notification generation.
                    display_thankyou = True
                    
                    completed_date = datetime.datetime.now()
                    Session.objects.filter(session_id=session.session_id).update(end_date=completed_date)
                    
                    summary_tasks = Session_Task.objects.filter(session=session).order_by('order')
                    counter = 1
                    for next_task in summary_tasks:
                        next_task_instances = Session_Task_Instance.objects.filter(session_task=next_task).aggregate(count_instances=Count('session_task_instance_id'))
                        session_summary += "<tr><td>" + str(counter) + "</td><td>" + next_task.task.name + "</td><td>" + str(next_task_instances['count_instances']) + "</td></tr>"
                        counter += 1
                    
                    # Trigger notifications that are linked to session completion
                    notify.generate_notifications(subject, "onSessionComplete")
                    
                else:
                    active_session_task_id = active_task[0].session_task_id
                    active_task = active_task[0].task
                    responses_dict = {}
                    active_task_responses = Session_Response.objects.filter(session_task_instance__session_task__session=session, session_task_instance__session_task__task=active_task).order_by('session_task_instance__session_task__order')
                    for response in active_task_responses:
                        if response.session_task_instance not in responses_dict:
                            responses_dict[response.session_task_instance] = response
                    
                    active_task_instance_values = Session_Task_Instance_Value.objects.filter(session_task_instance__session_task__session=session, session_task_instance__session_task__task=active_task, task_field__field_type__name='display').order_by('session_task_instance','task_field')
                    
                    # Add an attribute for each task, defining it as serial or not
                    if active_task.name_id == "stroop":
                        serial_instances = True
                        first_instance_id = str(active_task_instance_values[0].session_task_instance.session_task_instance_id)
                        serial_startslide = "<div class='space-bottom-med space-top-med stroop-slide'><div style='font-size: 72px;'>&nbsp;</div><button type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: stroopTaskBegin(this);'>Start</button><input class='form-field' type='hidden' id='response_audio_" + first_instance_id + "' name='response_audio_" + first_instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + first_instance_id + "' /></div>"
                        requires_audio = True
                    
                    count_inst = 0
                    for instance_value in active_task_instance_values:

                        # Determine how to display the value based on the field type
                        display_field = ""
                        response_field = ""
                        field_data_type = instance_value.task_field.field_data_type.name
                        
                        # Construct style attributes string from the specified field data attributes
                        field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=instance_value.task_field)
                        style_attributes = ";".join([str(attr.name) + ": " + str(attr.value) for attr in field_data_attributes])

                        session_task_instance = instance_value.session_task_instance
                        instance_id = str(instance_value.session_task_instance.session_task_instance_id)
                        
                        if field_data_type == "text":
                            display_field = instance_value.value.replace('\n', '<br>')
                        elif field_data_type == "text_well":
                            display_field = "<div class='well well-lg space-bottom-small'>" + instance_value.value.replace('\n', '<br>') + "</div>"
                        elif field_data_type == "image":
                            display_field = "<img src='" + STATIC_URL + "img/" + instance_value.value + "' style=\"" + style_attributes + "\" />"
                        elif field_data_type == "text_withblanks":
                            display_field = (instance_value.value).replace("[BLANK]", "<input class='form-field' name='response' type='text' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />")
                        elif field_data_type == "timer_rig":
                        
                            # Parse out the duration of the timer
                            timer_duration = re.compile(r"\[timer_([0-9]+)(min|sec)\]")
                            instance_duration = timer_duration.findall(instance_value.value)
                            if instance_duration:
                                dur_sec = instance_duration[0][0]
                                dur_unit = instance_duration[0][1]
                                if dur_unit is 'min':
                                    dur_sec = dur_sec * 60
                            else:
                                # Default duration
                                dur_sec = 60
                                
                            display_field = re.sub(timer_duration, "<br /><br /><button type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: startTimerRig(this, " + instance_id + ");'>Start</button><br />", instance_value.value)
                            
                            # Associated textarea where the user will type out the RIG response
                            display_field += "<div class='timer_display' id='timer_display_" + instance_id + "'>01:00</div><input type='hidden' id='timer_val_" + instance_id + "' value='" + dur_sec + "' /><textarea class='form-control form-field input-disabled' name='response' readonly='readonly' style=\"" + style_attributes + "\"></textarea><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
                        elif field_data_type == "text_newlines":
                            sents = instance_value.value.split(" || ")
                            regex_nonalpha = re.compile(r"^[^a-zA-Z0-9]+$")
                            display_field = "<br>".join([sent[0].lower() + sent[1:] for sent in sents if not regex_nonalpha.findall(sent)])
                        elif field_data_type == "text_stroop":
                            # Each instance should be displayed on its own, serially, with JS 'next' buttons in between
                            # HTML/JS: Display each instance in a div with class 'invisible', and add a JS function on 'next' button click
                            # which would hide the current div and display the next. If there is no next div, stop the audio recording
                            # and make the submit button active.
                            
                            # Since this is a Stroop task, determine the colour in which the word stimulus should be displayed
                            word_stimulus,colour_stimulus = instance_value.value.split("|")
                            colour_hex = colour_lookup[colour_stimulus]
                            
                            append_audio_response = ""
                            if count_inst+1 < len(active_task_instance_values):
                                next_instance_id = str(active_task_instance_values[count_inst+1].session_task_instance.session_task_instance_id)
                                if next_instance_id:
                                    append_audio_response = "<div class='invisible status_recording' style='margin-top: 5px;'><img src='" + STATIC_URL + "img/ajax_loader.gif' /> <span class='status_recording_msg small'></div><input class='form-field' type='hidden' id='response_audio_" + next_instance_id + "' name='response_audio_" + next_instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + next_instance_id + "' />"
                            
                            serial_startslide += "<div class='invisible stroop-slide'><div style='font-size: 72px; font-weight: bold; color: #" + colour_hex + ";'>" + word_stimulus.upper() + "</div><button type='button' class='btn btn-success btn-med btn-fixedwidth recording' onClick='javascript: stroopTaskNextItem(this);'>Next</button>" + append_audio_response + "</div>"
                        else:
                            display_field = instance_value.value.replace('\n', '<br>')
                        
                        
                        # Find associated response field data type
                        
                        if not instance_value.task_field.embedded_response:
                            response_field = Session_Response.objects.filter(session_task_instance=instance_value.session_task_instance)[0]
                            if response_field.date_completed:
                                existing_responses = True
                                
                            input_field = Task_Field.objects.get(task=active_task, field_type__name='input')
                            field_data_type = input_field.field_data_type.name
                            
                            # Construct style attributes string from the specified field data attributes
                            field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=input_field)
                            style_attributes = ";".join([str(attr.name) + ": " + str(attr.value) for attr in field_data_attributes])
                            
                            # regex for field data type 'scale' (scale_{from}_{to})
                            regex_scale = re.compile(r'scale\_([0-9]+)\_([0-9]+)')
         
                            if field_data_type == "multiselect":
                                existing_value = ""
                                if response_field.value_text:
                                    existing_value = response_field.value_text 
                                response_field = "<input class='form-field form-control' name='response' type='text' value='" + existing_value + "'><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
                            elif field_data_type == "text":
                                existing_value = ""
                                if response_field.value_text:
                                    existing_value = response_field.value_text 
                                response_field = "<input class='form-field form-control' name='response' type='text' value='" + existing_value + "' style=\"" + style_attributes + "\"><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
                            elif field_data_type == "textarea":
                                existing_value = ""
                                if response_field.value_text:
                                    existing_value = response_field.value_text 
                                response_field = "<textarea class='form-field form-control' name='response' style=\"" + style_attributes + "\">" + existing_value + "</textarea><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
                            elif field_data_type == "audio":
                                requires_audio = True
                                
                                # If the display field is to be kept visible during the audio the subject provides, keep it visible and directly show a recording button
                                keep_visible = instance_value.task_field.keep_visible
                                response_field = ""
                                if not keep_visible:
                                    response_field += "<p><input class='btn btn-primary btn-med btn-fixedwidth' type='button' onClick='javascript: hideDisplay(this);' value='Continue'></p>"
                                response_field += "<p id='record-btn_" + instance_id + "'"
                                if not keep_visible:
                                    response_field += " class='invisible'"
                                response_field += "><input id='btn_recording_" + instance_id + "' type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: toggleRecording(this);' value='Start recording'>&nbsp;<span class='invisible' id='status_recording_" + instance_id + "'><img src='" + STATIC_URL + "img/ajax_loader.gif' /> <span id='status_recording_" + instance_id + "_msg'></span></span><input class='form-field' type='hidden' id='response_audio_" + instance_id + "' name='response_audio_" + instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' /></p>"
                                    
                            elif field_data_type == "select":
                                existing_value = ""
                                if response_field.value_text:
                                    existing_value = response_field.value_text
                                response_field = ""
                                
                                # Get associated values for the select options.
                                sel_options = Session_Task_Instance_Value.objects.filter(session_task_instance=instance_value.session_task_instance,task_field__field_type__name='input').order_by('session_task_instance_value_id')
                                
                                for sel_option in sel_options:
                                    response_field += "<div class='radio'>"
                                    response_field += "<label><input type='radio' class='form-field' name='response_" + instance_id + "' value='" + sel_option.value + "'"
                                    
                                    # Mark any previously-submitted responses as selected
                                    if existing_value == sel_option.value:
                                        response_field += " selected='selected'"
                                        
                                    response_field += "> " + sel_option.value_display + "</label>"
                                    response_field += "</div>"
                                
                                response_field += "<input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
                            
                            elif regex_scale.findall(field_data_type):
                                matches = regex_scale.findall(field_data_type)
                                scale_start = matches[0][0]
                                scale_end = matches[0][1]
                                
                                response_field = "<div class='row'><div class='col-xs-6'><div class='scale_" + str(scale_start) + "_" + str(scale_end) + "' style=\"" + style_attributes + "\"></div><div class='scale_display' style='font-size: 20px;'></div><input class='form-field' name='response' type='hidden' value='' /></div></div><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />" 
                                
                        active_instances += [display_field + "<br/>" + response_field]
                        count_inst += 1
                        
            else:
                # The session has been completed. Display a summary.
                summary_tasks = Session_Task.objects.filter(session=session).order_by('order')
                counter = 1
                for next_task in summary_tasks:
                    next_task_instances = Session_Task_Instance.objects.filter(session_task=next_task).aggregate(count_instances=Count('session_task_instance_id'))
                    session_summary += "<tr><td>" + str(counter) + "</td><td>" + next_task.task.name + "</td><td>" + str(next_task_instances['count_instances']) + "</td></tr>"
                    counter += 1
                    
            passed_vars = {'session': session, 'num_current_task': num_current_task, 'num_tasks': num_tasks, 'percentage_completion': min(100,round(num_current_task*100.0/num_tasks)), 'active_task': active_task, 'active_session_task_id': active_session_task_id, 'serial_instances': serial_instances, 'serial_startslide': serial_startslide, 'active_instances': active_instances, 'requires_audio': requires_audio, 'existing_responses': existing_responses, 'completed_date': completed_date, 'session_summary': session_summary, 'display_thankyou': display_thankyou, 'user': request.user, 'is_authenticated': is_authenticated, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications}
            passed_vars.update(global_passed_vars)
                    
            return render_to_response('datacollector/session.html', passed_vars, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(website_root)
    else:
        return HttpResponseRedirect(website_root)


def results(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    # Get all associated responses from the database
    # TODO
    
    passed_vars = {'subject': subject}
    passed_vars.update(global_passed_vars)
    
    return render_to_response('datacollector/result.html', passed_vars)

def audiorecord(request):
    
    if request.user.is_authenticated():
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            if request.method == "POST":
                # Get the audio data, save it as a wav file 
                # to the server media directory, 
                # and return a success message

                msg = "Received " + ", ".join(request.POST.keys())
                files = "Received " + ", ".join(request.FILES.keys())
                instanceid = request.POST['instanceid']
                instance = Session_Task_Instance.objects.filter(session_task_instance_id=instanceid)
                session_response = None
                if instance:
                    instance = instance[0]
                    session_response = Session_Response.objects.filter(session_task_instance=instance)
                    if session_response:
                        session_response = session_response[0]
                
                    
                for f in request.FILES:
                    # Upload to responses
                    if session_response:
                        file_content = ContentFile(request.FILES[f].read())
                        session_response.value_audio.save('',file_content)
                        
                        # Update the Session Response date of completion
                        Session_Response.objects.filter(session_task_instance=instance).update(date_completed=datetime.datetime.now())
                
                return_dict = {"status": "success", "msg": msg, "files": files}
                json = simplejson.dumps(return_dict)
                return HttpResponse(json, mimetype="application/x-javascript")
        
    return HttpResponseRedirect(website_root)

def account(request):
    is_authenticated = False
    form_values = {}
    form_errors = []
    save_confirm = False
    save_msg = ""
    json_data = {}
    json_data['status'] = 'fail'
    json_data['email_change'] = 'false'
    active_notifications = []
    
    # These two flags are passed to the account page so that the base template included therein can use them
    consent_submitted = False
    demographic_submitted = False
    is_email_validated = False
    email_confirm_display = "<div class=\"alert alert-success\"><span class=\"glyphicon glyphicon-ok\"></span> Verified</div>"
    
    if request.user.is_authenticated():
        is_authenticated = True
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted
            is_email_validated = subject.email_validated
            
            # Fetch all notifications that are active and have not been dismissed by the user 
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = notify.get_active_new(subject)
            
            if request.method == "GET":
                # A get form request
                if 'resend-email' in request.GET:
                    # Initiate an email validation resend email if the user has provided an email
                    if request.user.email:
                        # Check if there is an existing email token, if not generate one
                        if subject.email_token:
                            email_token = subject.email_token
                        else:
                            email_token = crypto.generate_confirmation_token(request.user.username + request.user.email)
                        confirmation_link = website_hostname + "/activate/" + email_token  
                            
                        emailText = "You have updated your email address on " + global_passed_vars['website_name'] + "\n\nPlease click this link to confirm your email address:\n\n<a href=\"" + confirmation_link + "\">" + confirmation_link + "</a>\n\nWhy am I receiving this email? We value your privacy and want to make sure that you are the one who entered this email address in our system. If you received this email by mistake, you can make it all go away by simply ignoring it."
                        
                        emailHtml = """<h2 style="Margin-top: 0;color: #44a8c7;font-weight: 700;font-size: 24px;Margin-bottom: 16px;font-family: Lato,sans-serif;line-height: 32px;text-align: center">You have updated your email address on """ + global_passed_vars['website_name'] + """</h2>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><strong>Please click this link to confirm your email address:</strong></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><u><a href=\"""" + confirmation_link + """\">""" + confirmation_link + """</a></u></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">If the link above does not work, please copy and paste it into your browser's address bar.</p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><strong>Why am I receiving this email?</strong>\r\n We value your privacy and want to make sure that you are the one who entered this email address in our system. If you received this email by mistake, you can make it all go away by simply ignoring it.</p>\r\n"""
                        
                        successFlag = emails.sendEmail(email_username, email_name, [request.user.email], [], [], global_passed_vars['website_name'] + " - Email Confirmation", emailText, emails.emailPre + emailHtml + emails.emailPost)
                        if successFlag:
                            json_data['status'] = 'success'
                            
                            # Update database to keep a record of sent emails, if the mailer was successful
                            Subject_Emails.objects.create(date_sent=datetime.datetime.now().date(), subject=subject, email_from=email_username, email_to=request.user.email, email_type='email_confirmation')
                        else:
                            json_data['error'] = 'The confirmation email could not be sent. Please verify that you have provided a valid email address.'
                    else:
                        json_data['error'] = 'The confirmation email could not be sent. You have not provided an email address.'
                    
                    return HttpResponse(json.dumps(json_data))
                    
            if request.method == "POST":
                form_values = request.POST
                if 'btn-pwdchange' in request.POST:
                    # Perform form validation first
                    # Check that (1) the current password is correct, (2) the new password match, 
                    # (3) the new password meets the password field requirements
                    pwd_new = ""
                    if not 'pwd_current' in request.POST or not request.POST['pwd_current']:
                        form_errors += ['You did not provide your current password.']
                    elif not authenticate(username=User.objects.get(id=subject.user_id).username, password=request.POST['pwd_current']):
                        form_errors += ['The current password you provided is incorrect.']
                    
                    if not 'pwd_new1' in request.POST or not 'pwd_new2' in request.POST or \
                        not request.POST['pwd_new1'] or not request.POST['pwd_new2']:
                        form_errors += ['You did not provide your new password (twice).']
                    elif str(request.POST['pwd_new1']) != str(request.POST['pwd_new2']):
                        form_errors += ['The new passwords you provided do not match. You have to repeat the new password twice.']
                    
                    if not form_errors:
                        pwd_new = request.POST['pwd_new1']
                        u = User.objects.get(id=subject.user_id)
                        u.set_password(pwd_new)
                        u.save()
                        save_confirm = True
                        save_msg = "Password updated successfully."
                        json_data['save_msg'] = save_msg
                        json_data['status'] = 'success'
                    else:
                        json_data['error'] = [dict(msg=x) for x in form_errors]
                    
                    return HttpResponse(json.dumps(json_data))
                    
                elif 'btn-save' in request.POST:
                    
                    # Perform form validation first
                    # - check that if any of the email-related options has been selected, the email address is provided
                    user_email = ""
                    if 'email_address' in request.POST:
                        user_email = request.POST['email_address']
                        if user_email:
                            # Validate user email if provided
                            if not regex_email.match(user_email):
                                form_errors += ['The e-mail address you provided does not appear to be valid.']
                        
                    # Dictionary of options which require a user email
                    options_req_email = {'cb_preference_prizes': 'prize draws',
                                         'cb_preference_email_reminders': 'scheduled e-mail reminders', 
                                         'cb_preference_email_updates': 'electronic communication regarding study outcomes'}
                    options_selected = set(options_req_email.keys()).intersection(set(request.POST.keys()))
                    if options_selected and not user_email:
                        connector = " || "
                        plur_s = ""
                        if len(options_selected) > 1: plur_s = "s"
                        options_selected_str = connector.join([options_req_email[opt] for opt in options_selected])
                        num_conn = options_selected_str.count(connector)
                        options_selected_str = options_selected_str.replace(connector, ", ", num_conn-1)
                        options_selected_str = options_selected_str.replace(connector, ", and ")
                            
                        form_errors += ['You did not provide an e-mail address. An e-mail address is required since you selected the following option' + plur_s + ': ' + options_selected_str + "."]
                        
                    # - check that an email reminder frequency is specified, if reminders are requested
                    if 'cb_preference_email_reminders' in request.POST and 'radio_email_reminders_freq' not in request.POST:
                        form_errors += ['You have not selected a frequency for the scheduled e-mail reminders.']
                    
                    if not form_errors:
                        
                        current_email = User.objects.filter(id=request.user.id)[0].email
                        if user_email != current_email:
                            json_data['email_change'] = 'true'
                        
                        if user_email:
                            # If the email is different from the existing email for the account, reset the email validated flag, regenerate the email token, and resend a confirmation email
                            if user_email != current_email:
                                new_email_token = crypto.generate_confirmation_token(request.user.username + user_email)
                                Subject.objects.filter(user_id=request.user.id).update(email_validated=0, email_token=new_email_token)
                                
                                confirmation_link = website_hostname + "/activate/" + new_email_token
                                emailText = "You have updated your email address on " + global_passed_vars['website_name'] + "\n\nPlease click this link to confirm your email address:\n\n<a href=\"" + confirmation_link + "\">" + confirmation_link + "</a>\n\nWhy am I receiving this email? We value your privacy and want to make sure that you are the one who entered this email address in our system. If you received this email by mistake, you can make it all go away by simply ignoring it."
                                emailHtml = """<h2 style="Margin-top: 0;color: #44a8c7;font-weight: 700;font-size: 24px;Margin-bottom: 16px;font-family: Lato,sans-serif;line-height: 32px;text-align: center">You have updated your email address on """ + global_passed_vars['website_name'] + """</h2>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><strong>Please click this link to confirm your email address:</strong></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><u><a href=\"""" + confirmation_link + """\">""" + confirmation_link + """</a></u></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">If the link above does not work, please copy and paste it into your browser's address bar.</p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><strong>Why am I receiving this email?</strong>\r\n We value your privacy and want to make sure that you are the one who entered this email address in our system. If you received this email by mistake, you can make it all go away by simply ignoring it.</p>\r\n"""
                                
                                successFlag = emails.sendEmail(email_username, email_name, [user_email], [], [], global_passed_vars['website_name'] + " - Email Confirmation", emailText, emails.emailPre + emailHtml + emails.emailPost)
                                
                                # Update database to keep a record of sent emails, if the mailer was successful
                                if successFlag:
                                    s = Subject.objects.get(user_id=request.user.id)
                                    Subject_Emails.objects.create(date_sent=datetime.datetime.now().date(), subject=s, email_from=email_username, email_to=user_email, email_type='email_confirmation')
                                
                                # Display "Not verified" msg to user
                                email_confirm_display = "<button type=\"button\" class=\"btn btn-default btn-lg btn-red\" onClick=\"javascript: resendConfirmationEmail(this);\"><span class=\"glyphicon glyphicon-remove\" aria-hidden=\"true\"></span> Not verified. Click to resend confirmation email.</button>"
                                
                            User.objects.filter(id=request.user.id).update(email=user_email)
                        else:
                            User.objects.filter(id=request.user.id).update(email="")
                            
                            # Reset the email validation flag and the email token
                            Subject.objects.filter(user_id=request.user.id).update(email_validated=0, email_token=None)
                            
                            # Hide email verified msg
                            email_confirm_display = ""
                            
                        
                        subject = Subject.objects.get(user_id=request.user.id)
                        today = datetime.datetime.now().date()
                        existing_notif_prizes = Subject_Notifications.objects.filter(Q(date_end__isnull=True) | Q(date_end__gte = today), subject=subject, notification__notification_id="monthlyprize_eligibility")
                        if 'cb_preference_prizes' in request.POST:
                            subject.preference_prizes = 1
                            subject.email_prizes = user_email
                            subject.save()
                            
                            # Trigger notification generation for the user, as they may now be eligible for prizes 
                            # (i.e. new notifications to be displayed).
                            if existing_notif_prizes:
                                notify.update_notifications(subject, existing_notif_prizes)
                            else:
                                notify.generate_notifications(subject, "onSessionComplete")
                                
                        else:
                            subject.preference_prizes = 0
                            subject.email_prizes = None
                            subject.save()
                            
                            # The user is no longer eligible for prizes - trigger a notification update (for existing notifications)
                            # if there is an existing monthly prize notification
                            if existing_notif_prizes:
                                notify.update_notifications(subject, existing_notif_prizes)
                        
                        if 'cb_preference_email_reminders' in request.POST:
                            Subject.objects.filter(user_id=request.user.id).update(preference_email_reminders=1, email_reminders=user_email, preference_email_reminders_freq=request.POST['radio_email_reminders_freq'])
                        else:
                            Subject.objects.filter(user_id=request.user.id).update(preference_email_reminders=0, email_reminders=None, preference_email_reminders_freq=None)
                        
                        if 'cb_preference_email_updates' in request.POST:
                            Subject.objects.filter(user_id=request.user.id).update(preference_email_updates=1, email_updates=user_email)
                        else:
                            Subject.objects.filter(user_id=request.user.id).update(preference_email_updates=0, email_updates=None)
                        
                        save_confirm = True
                        save_msg = "Changes saved successfully."
                        json_data['save_msg'] = save_msg
                        json_data['email_confirm_display'] = email_confirm_display
                        json_data['status'] = 'success'
                    else:
                        json_data['error'] = [dict(msg=x) for x in form_errors]
                    
                    return HttpResponse(json.dumps(json_data))
                    
                elif 'btn-withdraw' in request.POST:
                    if 'withdraw_confirm' not in request.POST:
                        form_errors += ['You did not select the confirmation checkbox which acknowledges that you understand the effects of withdrawing from the study.']
                    
                    if not form_errors:
                        # Delete entire user account, including from auth_user
                        Subject.objects.filter(user_id=request.user.id).delete()
                        User.objects.filter(id=request.user.id).delete()
                        auth_logout(request)
                        json_data['status'] = 'success'
                        json_data['website_root'] = '/' + global_passed_vars['website_id']
                    else:
                        json_data['error'] = [dict(msg=x) for x in form_errors]
                    return HttpResponse(json.dumps(json_data))
                        
            else:
                # Fill out the form values with the default values from the database (i.e. mimic the way a POST form works - checkboxes only appear in the collection if they are checked).
                if subject.preference_prizes:
                    form_values['cb_preference_prizes'] = subject.preference_prizes
                if subject.preference_email_reminders:
                    form_values['cb_preference_email_reminders'] = subject.preference_email_reminders
                    form_values['radio_email_reminders_freq'] = subject.preference_email_reminders_freq
                if subject.preference_email_updates:
                    form_values['cb_preference_email_updates'] = subject.preference_email_updates
                form_values['email_address'] = request.user.email
            
            passed_vars = {'is_authenticated': is_authenticated, 'user': request.user, 'form_values': form_values, 'form_errors': form_errors, 'save_confirm': save_confirm, 'save_msg': save_msg, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications, 'is_email_validated': is_email_validated}
            passed_vars.update(global_passed_vars)
            return render_to_response('datacollector/account.html', passed_vars, context_instance=RequestContext(request))
        else:
            # If user is authenticated with as a User that doesn't exist as a Subject (i.e. for this study), then go to main page
            return HttpResponseRedirect(website_root)
    else:
        # If user is not authenticated, just go to main page
        return HttpResponseRedirect(website_root)
        
        
def about(request):
    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    active_notifications = []
    
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
        
    passed_vars = {'is_authenticated': is_authenticated, 'user': request.user, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications}
    passed_vars.update(global_passed_vars)
    
    return render_to_response('datacollector/about.html', passed_vars, context_instance=RequestContext(request))

def error(request, error_id):
    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    active_notifications = []
    
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
    
    passed_vars = {'error_id': error_id, 'is_authenticated': is_authenticated, 'user': request.user, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications}
    passed_vars.update(global_passed_vars)
    
    return render_to_response('datacollector/error.html', passed_vars, context_instance=RequestContext(request))
    
    
def pagetime(request):
    
    if request.method == "POST":
        
        session_task_id = request.POST['sessiontaskid']
        time_elapsed = request.POST['timeelapsed']
        
        # Save to db
        current_task = Session_Task.objects.filter(session_task_id=session_task_id)
        if current_task:
            current_time_elapsed = current_task[0].total_time
            current_task.update(total_time=int(current_time_elapsed) + int(time_elapsed))
        
        return_dict = {"status": "success"}
        json = simplejson.dumps(return_dict)
        return HttpResponse(json, mimetype="application/x-javascript")
    return HttpResponseRedirect(website_root)
    
    
@csrf_exempt
def bundle_completion_validate(request):
    # Takes: POST request with parameters "username" and "confirmation_token"
    # Returns: JSON with parameters "status" ("success"/"fail"), "valid" ("yes"/"no")
    json_data = {"status": "success"}
    is_valid = False
    today = datetime.datetime.now().date()
    
    if request.method == "POST":
        if "username" in request.POST and "completion_token" in request.POST:
            username = request.POST["username"]
            completion_token = request.POST["completion_token"]
            if username and completion_token and len(completion_token) == 128 and completion_token.isalnum():
                
                # Check user exists
                u = User.objects.filter(username=username)
                if u:
                    u = u[0]
                    # Check associated subject exists
                    s = Subject.objects.filter(user_id=u.id)
                    if s:
                        s = s[0]
                        # Check if token exists in database for a Subject_Bundle pair for the same subject, and that it hasn't been used before
                        sb = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), active_startdate__lte=today, completion_token=completion_token, subject=s, completion_token_usedate__isnull=True)
                        if sb:
                            sb = sb[0]
                            # Check if the subject has completed all required sessions
                            completed_sessions = Session.objects.filter(subject=s, end_date__isnull=False, start_date__gte=sb.active_startdate)
                            if completed_sessions and (not sb.completion_req_sessions or len(completed_sessions) >= sb.completion_req_sessions):
                                is_valid = True
    
        if is_valid:
            json_data["valid"] = "yes"
        else:
            json_data["valid"] = "no"
        json = simplejson.dumps(json_data)
        
        response = HttpResponse(json)
        response["Content-type"] = "application/json"
        response["Access-Control-Allow-Origin"] = "*" # https://tasks.crowdflower.com
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Accept, Content-Type, X-CSRFToken, X-Requested-With"
        return response
    return HttpResponse("Unauthorized", status=401)