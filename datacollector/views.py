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
from datacollector.forms import *
from datacollector.models import *

import datetime
import random
import re


# Globals
global global_passed_vars
global_passed_vars = { "website_name": "DementiaWeb", "website_email": "dementiaweb.toronto@gmail.com" }

def index(request):
    
    # Authenticate current user. If no user logged in, redirect to login page.
    is_authenticated = False
    completed_sessions = []
    active_sessions = []
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
    
    if request.user.is_authenticated():
        is_authenticated = True

        if request.method == 'POST':
            date_submitted = datetime.datetime.now()
            form_type = request.POST['form_type']
            if form_type == 'consent':
                # If consent has been provided, update the database for the subject
                # and reload the page
                if 'radio_consent' in request.POST:
                    Subject.objects.filter(user_id=request.user.id).update(date_consent_submitted=date_submitted)
                    if request.POST['radio_consent'] == 'alternate':
                        Subject.objects.filter(user_id=request.user.id).update(consent_alternate=1)
                
                # Preference for allowing public release of collected data
                if 'cb_preference_public_release' in request.POST:
                    Subject.objects.filter(user_id=request.user.id).update(preference_public_release=1)
                    
                # Preference for receiving email reminders about completing sessions
                if 'cb_preference_email_reminders' in request.POST:
                    
                    user_email = ""
                    if 'preference_email_reminders' in request.POST:
                        user_email = request.POST['preference_email_reminders']
                        reminders_freq = request.POST['radio_email_reminders_freq']
                        
                        # TODO: some kind of email validation
                        if user_email:
                            Subject.objects.filter(user_id=request.user.id).update(preference_email_reminders=1,preference_email_reminders_freq=reminders_freq,email_reminders=user_email)
                    
                # Preference for receiving email updates about related future research/publications
                if 'cb_preference_email_updates' in request.POST:
                    
                    user_email = ""
                    if 'preference_email_updates' in request.POST:
                        user_email = request.POST['preference_email_updates']
                        
                        # TODO: some kind of email validation
                        if user_email:
                            Subject.objects.filter(user_id=request.user.id).update(preference_email_updates=1,email_updates=user_email)
            
            elif form_type == 'demographic':
                # Gender 
                if 'gender' in request.POST:
                    response_gender = request.POST['gender']
                    selected_gender = Gender.objects.filter(gender_id=response_gender)
                    if selected_gender:
                        selected_gender = selected_gender[0]
                        Subject.objects.filter(user_id=request.user.id).update(gender=selected_gender)
                
                # DOB
                if 'dob' in request.POST:
                    selected_dob = request.POST['dob']
                    
                    # TODO: check that date is within range -150:-18 (i.e., at least 18 years old)
                    Subject.objects.filter(user_id=request.user.id).update(dob=selected_dob)
                
                # Ethnicity
                if 'ethnicity' in request.POST:
                    response_ethnicity = request.POST.getlist('ethnicity')
                    for i in range(len(response_ethnicity)):
                        selected_ethnicity = Ethnicity.objects.filter(ethnicity_id=response_ethnicity[i])
                        if selected_ethnicity:
                            selected_ethnicity = selected_ethnicity[0]
                        
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
                        
                        selected_language = Language.objects.filter(language_id=response_languages[i])
                        if selected_language:
                            selected_language = selected_language[0]
                        
                        subject = Subject.objects.filter(user_id=request.user.id)
                        if subject:
                            subject = subject[0]
                        
                        lang_exists = Subject_Language.objects.filter(subject=subject, language=selected_language)
                        
                        lang_level = None
                        if 'language_fluency_' + str(response_languages[i]) in request.POST:
                            lang_level = Language_Level.objects.filter(language_level_id=request.POST['language_fluency_' + str(response_languages[i])])
                            if lang_level:
                                lang_level = lang_level[0]
                        
                        # TODO: raise an error if lang level not selected
                        if not lang_level:
                            lang_level = Language_Level.objects.filter(name='native')
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
                            selected_language = Language.objects.filter(language_id=sel_response_language)
                            if selected_language:
                                selected_language = selected_language[0]
                            
                            subject = Subject.objects.filter(user_id=request.user.id)
                            if subject:
                                subject = subject[0]
                            
                            lang_exists = Subject_Language.objects.filter(subject=subject, language=selected_language)
                            
                            lang_level = None
                            if 'other_fluency_' + str(i) in request.POST:
                                lang_level = Language_Level.objects.filter(language_level_id=request.POST['other_fluency_' + str(i)])
                                if lang_level:
                                    lang_level = lang_level[0]
                            
                            # TODO: raise an error if lang level not selected
                            if not lang_level:
                                lang_level = Language_Level.objects.filter(name='native')
                                if lang_level:
                                    lang_level = lang_level[0]
                            
                            if not lang_exists:
                                Subject_Language.objects.create(subject=subject, language=selected_language, level=lang_level)
                            else:
                                Subject_Language.objects.filter(subject=subject, language=selected_language).update(level=lang_level)
                                
                
                # Education level
                if 'education_level' in request.POST:
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
                        
                        dementia_type_exists = Subject_Dementia_Type.objects.filter(subject=subject, dementia_type=selected_dementia_type)
                        if not dementia_type_exists:
                            Subject_Dementia_Type.objects.create(subject=subject, dementia_type=selected_dementia_type, dementia_type_name=selected_dementia_name)
                
                # Dementia meds 
                if 'dementia_med' in request.POST:
                    response_dementia_med = request.POST['dementia_med']
                    map_response_to_id = { 'yes': 1, 'no': 0}
                    if response_dementia_med in map_response_to_id:
                        response_dementia_med_id = map_response_to_id[response_dementia_med]
                        Subject.objects.filter(user_id=request.user.id).update(dementia_med=response_dementia_med_id)
                        
                # Smoking 
                if 'smoking' in request.POST:
                    response_smoking = request.POST['smoking']
                    map_response_to_id = { 'yes': 1, 'no': 0}
                    if response_smoking in map_response_to_id:
                        response_smoking_id = map_response_to_id[response_smoking]
                        Subject.objects.filter(user_id=request.user.id).update(smoker_recent=response_smoking_id)
                
                # Set the demographic flag to 1
                Subject.objects.filter(user_id=request.user.id).update(date_demographics_submitted=date_submitted)
                
        # Assume that every authenticated user exists in datacollector subject. If they don't, add them with the appropriate ID, and all flags initialized to null/false.
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
        else:
            date_submitted = datetime.datetime.now()
            subject = Subject.objects.create(user_id=request.user.id, date_created=date_submitted, consent_alternate=0, preference_email_reminders=0, preference_email_updates=0, preference_public_release=0, preference_prizes=0)
        
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
    
        # For the currently logged on user, find all previous sessions in the system
        completed_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=False).order_by('-start_date')
        active_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=True).order_by('-start_date')
    
    passed_vars = {'is_authenticated': is_authenticated, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'completed_sessions': completed_sessions, 'active_sessions': active_sessions, 'user': request.user, 'gender_options': gender_options, 'language_options': language_options, 'language_other': language_other, 'language_fluency_options': language_fluency_options, 'ethnicity_options': ethnicity_options, 'education_options': education_options, 'dementia_options': dementia_options, 'country_res_options': country_res_options }
    passed_vars.update(global_passed_vars)
    return render_to_response('datacollector/index.html', passed_vars, context_instance=RequestContext(request))

def login(request):

    # If there is a currently logged in user, just redirect to home page
    if request.user.is_authenticated():
        return HttpResponseRedirect('/datacollector/')
    
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
                    return HttpResponseRedirect('/datacollector/')
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
    return HttpResponseRedirect('/datacollector/')


def register(request):

    # If there is a currently logged in user, just redirect to home page
    if request.user.is_authenticated():
        return HttpResponseRedirect('/datacollector/')
    
    # If the form has been submitted, validate the data and 
    errors = []
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_user = form.save()
            
            # Create a corresponding subject in the datacollector app
            new_subject = Subject.objects.create(user_id=new_user.id)

            return HttpResponseRedirect('/datacollector/')
    else:
        form = UserCreationForm()

    passed_vars = {'form': form}
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

        default_tasks = [1,2,7,8,10,11,12]     
        startdate = datetime.datetime.now()
        new_session = Session.objects.create(subject=subject, start_date=startdate, end_date=None)
        
        # Select random task questions for the session  
        for task_id in default_tasks:
            task = Task.objects.get(task_id=task_id)
            num_instances = task.default_num_instances
            task_order = task.default_order
            task_delay = task.default_delay
            task_embedded_delay = task.default_embedded_delay
            
            # Add the task to the current session in the database
            new_task = Session_Task.objects.create(session=new_session, task=task, order=task_order, delay=task_delay, embedded_delay=task_embedded_delay)

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
                        selected_values += [field_values[0]]
                    else:
                        # If there aren't any results, relax the query by restricting only to values that haven't been seen before
                        field_values = Task_Field_Value.objects.filter(task_field=field).exclude(value__in=existing_values)
                        if field_values:
                            selected_values += [field_values[0]]
                        else:
                            # If there still aren't any results (i.e., the subject has seen all possible values for this field), relax the query completely by selecting any random field value
                            field_values = Task_Field_Value.objects.filter(task_field=field)
                            if field_values:
                                selected_values += [field_values[0]]
                            else:
                                # The database doesn't contain any entries for this task field.
                                # Fail, display an error page.
                                return HttpResponseRedirect('/datacollector/error/501')
                    
                    # Build limit query with Q objects
                    selected_assoc_ids = [item.assoc_id for item in selected_values]
                    selected_ids = [item.task_field_value_id for item in selected_values]
                    limit_assoc = [~Q(task_field_value_id=i) for i in selected_assoc_ids if i]
                    limit_id = [~Q(task_field_value_id=i) for i in selected_ids if i]
                    limits = limit_assoc + limit_id
                
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
                    
        return HttpResponseRedirect('/datacollector/session/' + str(new_session.session_id))
    else:
        return HttpResponseRedirect('/datacollector/')


def session(request, session_id):
    
    if request.user.is_authenticated():
        session = Session.objects.filter(session_id=session_id)
        if session:
            session = session[0]

            # Update the date_last_session_access for the user (this drives reminder emails)
            date_access = datetime.datetime.now()
            Subject.objects.filter(user_id=request.user.id).update(date_last_session_access=date_access)
            
            # If the session is active, find the first unanswered task instance to display
            active_task = None
            active_instances = []   
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
                
                # If session responses are submitted, write them to the database first (no validation needed)
                if request.method == "POST":
                    
                    active_task = Session_Task.objects.filter(session=session,date_completed__isnull=True).order_by('order')[0].task

                    # Process any input, textarea (text), and multiselect responses
                    if 'response' in request.POST and 'instanceid' in request.POST:
                        responses = request.POST.getlist('response')
                        instances = request.POST.getlist('instanceid')
                        for i in range(len(responses)):
                            response = responses[i]
                            instance = Session_Task_Instance.objects.filter(session_task_instance_id=instances[i])
                            if instance:
                                instance = instance[0]
                                
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
                            response_label = 'response_' + str(instances[i])
                            if response_label in request.POST:
                                response = request.POST[response_label]
                                instance = Session_Task_Instance.objects.filter(session_task_instance_id=instances[i])
                                if instance:
                                    instance = instance[0]
                                    
                                    # Find the response field type for this task
                                    response_data_type = Task_Field.objects.filter(task=instance.session_task.task,field_type__name='input')[0].field_data_type
                                    
                                    if response_data_type == 'select':
                                        Session_Response.objects.filter(session_task_instance=instance).update(value_text=response,date_completed=datetime.datetime.now())
                                    else:
                                        Session_Response.objects.filter(session_task_instance=instance).update(value_text=response,date_completed=datetime.datetime.now())
                    
                    
                    # Mark the task as submitted
                    Session_Task.objects.filter(session=session,task=active_task).update(date_completed=datetime.datetime.now())


                num_current_task = Session_Task.objects.filter(session=session,date_completed__isnull=False).count() + 1
                num_tasks = Session_Task.objects.filter(session=session).count()  
                active_task = Session_Task.objects.filter(session=session,date_completed__isnull=True).order_by('order')
                if not active_task:
                    # All tasks in the current session have been completed - mark the session as complete with an end date stamp, and display acknowledgement. Display summary.
                    display_thankyou = True
                    
                    completed_date = datetime.datetime.now()
                    Session.objects.filter(session_id=session.session_id).update(end_date=completed_date)
                    
                    summary_tasks = Session_Task.objects.filter(session=session).order_by('order')
                    counter = 1
                    for next_task in summary_tasks:
                        next_task_instances = Session_Task_Instance.objects.filter(session_task=next_task).aggregate(count_instances=Count('session_task_instance_id'))
                        session_summary += "<tr><td>" + str(counter) + "</td><td>" + next_task.task.name + "</td><td>" + str(next_task_instances['count_instances']) + "</td></tr>"
                        counter += 1
                    
                else:
                    active_session_task_id = active_task[0].session_task_id
                    active_task = active_task[0].task
                    responses_dict = {}
                    active_task_responses = Session_Response.objects.filter(session_task_instance__session_task__session=session, session_task_instance__session_task__task=active_task).order_by('session_task_instance__session_task__order')
                    for response in active_task_responses:
                        if response.session_task_instance not in responses_dict:
                            responses_dict[response.session_task_instance] = response
                    
                    active_task_instance_values = Session_Task_Instance_Value.objects.filter(session_task_instance__session_task__session=session, session_task_instance__session_task__task=active_task, task_field__field_type__name='display').order_by('session_task_instance','task_field')

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
                        elif field_data_type == "image":
                            display_field = "<img src='/static/img/" + instance_value.value + "' style=\"" + style_attributes + "\" />"
                        elif field_data_type == "text_withblanks":
                            display_field = (instance_value.value).replace("[BLANK]", "<input name='response' type='text' value='' /><input name='instanceid' type='hidden' value='" + instance_id + "' />")
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
                                
                            display_field = re.sub(timer_duration, "<br /><button onClick='javascript: startTimerRig(this, " + instance_id + ");'>Start</button><br />", instance_value.value)
                            
                            # Associated textarea where the user will type out the RIG response
                            display_field += "<div class='timer_display' id='timer_display_" + instance_id + "'>01:00</div><input type='hidden' id='timer_val_" + instance_id + "' value='" + dur_sec + "' /><textarea name='response' readonly='readonly' style=\"" + style_attributes + "\"></textarea><input name='instanceid' type='hidden' value='" + instance_id + "' />"
                        else:
                            display_field = instance_value.value
                        
                        
                        # Find associated response field data type
                        
                        if not instance_value.task_field.embedded_response:
                            response_field = Session_Response.objects.filter(session_task_instance=instance_value.session_task_instance)[0]
                            if response_field.date_completed:
                                existing_responses = True
                                
                            input_field = Task_Field.objects.get(task=active_task, field_type__name='input')
                            field_data_type = input_field.field_data_type.name
                            
                            # Construct style attributes string from the specified field data attributes
                            field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=input_field)
                            style_attributes = ";".join([str(attr.name) + ": '" + str(attr.value) + "'" for attr in field_data_attributes])
         
                            if field_data_type == "multiselect":
                                existing_value = ""
                                if response_field.value_text:
                                    existing_value = response_field.value_text 
                                response_field = "<input name='response' type='text' value='" + existing_value + "'><input name='instanceid' type='hidden' value='" + instance_id + "' />"
                            elif field_data_type == "text":
                                existing_value = ""
                                if response_field.value_text:
                                    existing_value = response_field.value_text 
                                response_field = "<input name='response' type='text' value='" + existing_value + "'><input name='instanceid' type='hidden' value='" + instance_id + "' />"
                            elif field_data_type == "textarea":
                                existing_value = ""
                                if response_field.value_text:
                                    existing_value = response_field.value_text 
                                response_field = "<textarea name='response' style=\"" + style_attributes + "\">" + existing_value + "</textarea><input name='instanceid' type='hidden' value='" + instance_id + "' />"
                            elif field_data_type == "audio":
                                requires_audio = True
                                
                                # If the display field is to be kept visible during the audio the subject provides, keep it visible and directly show a recording button
                                keep_visible = instance_value.task_field.keep_visible
                                response_field = ""
                                if not keep_visible:
                                    response_field += "<p><input type='button' onClick='javascript: hideDisplay(this);' value='Continue'></p>"
                                response_field += "<p id='record-btn'"
                                if not keep_visible:
                                    response_field += " class='invisible'"
                                response_field += "><input type='button' onClick='javascript: toggleRecording(this);' value='Start recording'>&nbsp;<span id='status_recording'></span><input name='instanceid' type='hidden' value='" + instance_id + "' /></p>"
                                    
                            elif field_data_type == "select":
                                existing_value = ""
                                if response_field.value_text:
                                    existing_value = response_field.value_text
                                response_field = ""
                                
                                # Get associated values for the select options.
                                sel_options = Session_Task_Instance_Value.objects.filter(session_task_instance=instance_value.session_task_instance,task_field__field_type__name='input').order_by('session_task_instance_value_id')
                                
                                for sel_option in sel_options:
                                    response_field += "<input type='radio' name='response_" + instance_id + "' value='" + sel_option.value + "'"
                                    
                                    # Mark any previously-submitted responses as selected
                                    if existing_value == sel_option.value:
                                        response_field += " selected='selected'"
                                        
                                    response_field += "> " + sel_option.value_display + "<br />"
                                    
                                response_field += "<input name='instanceid' type='hidden' value='" + instance_id + "' />"
                        
                        active_instances += [display_field + "<br/>" + response_field]
                        
            else:
                # The session has been completed. Display a summary.
                summary_tasks = Session_Task.objects.filter(session=session).order_by('order')
                counter = 1
                for next_task in summary_tasks:
                    next_task_instances = Session_Task_Instance.objects.filter(session_task=next_task).aggregate(count_instances=Count('session_task_instance_id'))
                    session_summary += "<tr><td>" + str(counter) + "</td><td>" + next_task.task.name + "</td><td>" + str(next_task_instances['count_instances']) + "</td></tr>"
                    counter += 1
                    
            passed_vars = {'session': session, 'num_current_task': num_current_task, 'num_tasks': num_tasks, 'percentage_completion': min(100,round(num_current_task*100.0/num_tasks)), 'active_task': active_task, 'active_session_task_id': active_session_task_id, 'active_instances': active_instances, 'requires_audio': requires_audio, 'existing_responses': existing_responses, 'completed_date': completed_date, 'session_summary': session_summary, 'display_thankyou': display_thankyou, 'user': request.user}
            passed_vars.update(global_passed_vars)
                    
            return render_to_response('datacollector/session.html', passed_vars, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect('/datacollector/')
    else:
        return HttpResponseRedirect('/datacollector/')


def results(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    # Get all associated responses from the database
    # TODO
    
    passed_vars = {'subject': subject}
    passed_vars.update(global_passed_vars)
    
    return render_to_response('datacollector/result.html', passed_vars)

def audiotest(request):
    if request.method == "POST":
        # Get the audio data, save it as a wav file 
        # to the server media directory, 
        # and return a success message

        # Test: create a text file in the media directory
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
        
        return_dict = {"status": "success", "msg": msg, "files": files}
        json = simplejson.dumps(return_dict)
        return HttpResponse(json, mimetype="application/x-javascript")
    return render_to_response('datacollector/audiotest.html', context_instance=RequestContext(request))

def about(request):
    is_authenticated = False
    if request.user.is_authenticated():
        is_authenticated = True
        
    passed_vars = {'is_authenticated': is_authenticated, 'user': request.user}
    passed_vars.update(global_passed_vars)
    
    return render_to_response('datacollector/about.html', passed_vars, context_instance=RequestContext(request))

def error(request, error_id):
    is_authenticated = False
    if request.user.is_authenticated():
        is_authenticated = True
    
    passed_vars = {'error_id': error_id, 'is_authenticated': is_authenticated, 'user': request.user}
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
    return HttpResponseRedirect('/datacollector/')