# Create your views here.

from django import forms
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


def index(request):

    # Authenticate current user. If no user logged in, redirect to login page.
    is_authenticated = False
    completed_sessions = []
    active_sessions = []
    consent_submitted = False
    demographic_submitted = False
    
    if request.user.is_authenticated():
        is_authenticated = True

        if request.method == 'POST':
            form_type = request.POST['form_type']
            if form_type == 'consent':
                # If consent has been provided, update the database for the subject
                # and reload the page
                if 'cb_consent' in request.POST:
                    Subject.objects.filter(user_id=request.user.id).update(consent_submitted=1,preference_public_release=1)
                
                if 'cb_preference_email' in request.POST:
                    
                    user_email = ""
                    if 'preference_email' in request.POST:
                        user_email = request.POST['preference_email']
                    
                    Subject.objects.filter(user_id=request.user.id).update(preference_email_updates=1)
                    User.objects.filter(id=request.user.id).update(email=user_email)

            elif form_type == 'demographic':
                pass
            
        # Assume that every authenticated user exists in datacollector subject
        subject = Subject.objects.get(user_id=request.user.id)

        # If first time logging in, display Consent Form, and ask for consent
        consent_submitted = subject.consent_submitted
        demographic_submitted = subject.demographic_submitted
    
        # For the currently logged on user, find all previous sessions in the system
        completed_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=False).order_by('-start_date')
        active_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=True).order_by('-start_date')
    
    

    return render_to_response('datacollector/index.html', {'is_authenticated': is_authenticated, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'completed_sessions': completed_sessions, 'active_sessions': active_sessions }, context_instance=RequestContext(request))

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
    
    return render_to_response('datacollector/login.html', {'form': form, 'errors': errors}, context_instance=RequestContext(request))


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

    return render_to_response('datacollector/register.html', {'form': form}, context_instance=RequestContext(request))

def question(request, session_id, instance_id):
    return render_to_response('datacollector/question.html', {'session': session, 'subject': subject, 'task_instance': instance})


def startsession(request):
    # Begin a new session for the current user: set up the database tables, 
    # the task instances and the response fields.
    
    if request.user.is_authenticated():
        
        subject = Subject.objects.get(user_id=request.user.id)

        default_tasks = [1,2,6,7,8,9,10]        
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
            # (only for the display fields)
            task_fields_display = Task_Field.objects.filter(task=task,field_type__name='display')

            # For each display field, select random <num_instances> which the user hasn't seen before
            for field in task_fields_display:
                
                existing_values = Session_Task_Instance_Value.objects.filter(task_field=field, session_task_instance__session_task__session__subject=subject)
                field_values = Task_Field_Value.objects.filter(task_field=field).exclude(value__in=existing_values)
                
                # If there aren't sufficiently many values that the user hasn't seen before, 
                # or if the user has seen all of the available task instances, then just 
                # use the entire list of all possible values.
                if len(field_values) < num_instances:
                    field_values = Task_Field_Value.objects.filter(task_field=field)
                
                # Randomly select N task instances, and insert them into the session's task instance
                # values table in the database
                selected_values = random.sample(field_values, num_instances)
                for index_instance in range(num_instances):
                    instance_value = selected_values[index_instance]
                    new_session_value = Session_Task_Instance_Value.objects.create(session_task_instance=new_task_instances[index_instance], task_field=field, value=instance_value.value, difficulty=instance_value.difficulty)

        return HttpResponseRedirect('/datacollector/session/' + str(new_session.session_id))
    else:
        return HttpResponseRedirect('/datacollector/')


def session(request, session_id):
    
    if request.user.is_authenticated():
        session = Session.objects.filter(session_id=session_id)
        if session:
            session = session[0]

            # If the session is active, find the first unanswered task instance to display
            active_task = None
            active_instances = []   

            if not session.end_date:
                
                # If session responses are submitted, write them to the database first (no validation needed)
                if request.method == "POST":
                    
                    active_task = Session_Task.objects.filter(session=session,date_completed__isnull=True).order_by('order')[0].task

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
                    
                    # Mark the task as submitted
                    Session_Task.objects.filter(session=session,task=active_task).update(date_completed=datetime.datetime.now())


                num_current_task = Session_Task.objects.filter(session=session,date_completed__isnull=False).count() + 1
                num_tasks = Session_Task.objects.filter(session=session).count()  
                requires_audio = False
                active_task = Session_Task.objects.filter(session=session,date_completed__isnull=True).order_by('order')[0].task
                responses_dict = {}
                active_task_responses = Session_Response.objects.filter(session_task_instance__session_task__session=session, session_task_instance__session_task__task=active_task).order_by('session_task_instance__session_task__order')
                for response in active_task_responses:
                    if response.session_task_instance not in responses_dict:
                        responses_dict[response.session_task_instance] = response
                
                active_task_instance_values = Session_Task_Instance_Value.objects.filter(session_task_instance__session_task__session=session, session_task_instance__session_task__task=active_task).order_by('session_task_instance','task_field')

                for instance_value in active_task_instance_values:

                    # Determine how to display the value based on the field type
                    display_field = ""
                    response_field = ""
                    field_data_type = instance_value.task_field.field_data_type.name
                    
                    # Construct style attributes string from the specified field data attributes
                    field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=instance_value.task_field)
                    style_attributes = ";".join([str(attr.name) + "='" + str(attr.value) + "'" for attr in field_data_attributes])

                    session_task_instance = instance_value.session_task_instance
                    if field_data_type == "text":
                        display_field = instance_value.value.replace('\n', '<br>')
                    elif field_data_type == "image":
                        display_field = "<img src='/static/img/" + instance_value.value + "' " + style_attributes + ">"
                    elif field_data_type == "text_withblanks":
                        display_field = (instance_value.value).replace("[BLANK]", "<input type='text' value=''>")
                    else:
                        display_field = instance_value.value
                    
                    # Find associated response field data type
                    if not instance_value.task_field.embedded_response:
                        response_field = Session_Response.objects.filter(session_task_instance=instance_value.session_task_instance)[0]
                        input_field = Task_Field.objects.get(task=active_task, field_type__name='input')
                        field_data_type = input_field.field_data_type.name
                        
                        # Construct style attributes string from the specified field data attributes
                        field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=input_field)
                        style_attributes = ";".join([str(attr.name) + ": '" + str(attr.value) + "'" for attr in field_data_attributes])
     
                        instance_id = str(instance_value.session_task_instance.session_task_instance_id)
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
                            response_field = "<p><input type='button' onClick='javascript: toggleRecording(this);' value='Start recording'>&nbsp;<span id='status_recording'></span><input name='instanceid' type='hidden' value='" + instance_id + "' /></p>"
                    
                    active_instances += [display_field + "<br/>" + response_field]
                    

            return render_to_response('datacollector/session.html', {'session': session, 'num_current_task': num_current_task, 'num_tasks': num_tasks, 'percentage_completion': min(100,round(num_current_task*100.0/num_tasks)), 'active_task': active_task, 'active_instances': active_instances, 'requires_audio': requires_audio}, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect('/datacollector/')
    else:
        return HttpResponseRedirect('/datacollector/')


def results(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    # Get all associated responses from the database
    # TODO
    return render_to_response('datacollector/result.html', {'subject': subject})

def audiotest(request):
    if request.method == "POST":
        # Get the audio data, save it as a wav file 
        # to the server media directory, 
        # and return a success message

        # Test: create a text file in the media directory
        msg = "Received " + ", ".join(request.POST.keys())
        files = "Received " + ", ".join(request.FILES.keys())

        for f in request.FILES:
            # Upload to responses
            session_task_instance = Session_Task_Instance.objects.all()[0]
            #new_response = Session_Response.objects.create(session_task_instance=session_task_instance, value_audio=request.FILES[f])
            #new_response.save()
            file_content = ContentFile(request.FILES[f].read())
            Session_Response.objects.get(session_response_id=1).value_audio.save('',file_content)   


        return_dict = {"status": "success", "msg": msg, "files": files}
        json = simplejson.dumps(return_dict)
        return HttpResponse(json, mimetype="application/x-javascript")
    return render_to_response('datacollector/audiotest.html', context_instance=RequestContext(request))

def help(request):
    is_authenticated = False
    if request.user.is_authenticated():
        is_authenticated = True
    return render_to_response('datacollector/help.html', {'is_authenticated': is_authenticated}, context_instance=RequestContext(request))
