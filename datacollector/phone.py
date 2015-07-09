# Create views handling phone API

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson

from datacollector.views import generate_session
from datacollector.models import *
from csc2518.settings import STATIC_URL
from csc2518.settings import SUBSITE_ID

import datetime
import json


def session(request):
    json_data = {}
    json_data['status'] = "success"
    
    # Authenticate the request - has to be issued by a superuser
    if 'auth_name' in request.POST and 'auth_pass' in request.POST:
        username = request.POST['auth_name']
        password = request.POST['auth_pass']
        system_user = authenticate(username=username, password=password)
        if system_user is not None:
            if system_user.is_active and system_user.is_superuser:
                # If the user is a valid superuser, 
                # proceed with returning the active phone session for the requested user (if one exists),
                # or create a new session (if none exist).
                if 'user_passcode' in request.POST and 'user_birthyear' in request.POST and 'user_birthmonth' in request.POST and 'user_birthday' in request.POST:
                    # Validate user
                    user = Subject.objects.filter(user_id=request.POST['user_passcode'])
                    if user is not None:
                        user = user[0]
                        
                        # Validate user birth date to prevent random guessing of passcodes
                        birth_year = request.POST['user_birthyear']
                        birth_month = request.POST['user_birthmonth']
                        birth_day = request.POST['user_birthday']
                        if birth_year.isdigit() and birth_month.isdigit() and birth_day.isdigit():
                            birth_date = datetime.date(int(birth_year), int(birth_month), int(birth_day))
                            if user.dob and user.dob == birth_date:
                                
                                # Look for latest active *phone* session, if one exists (only one phone session is allowed to exist at a time)
                                session_type = Session_Type.objects.get(name='phone')
                                active_sess = Session.objects.filter(subject=user,session_type=session_type).order_by('-session_id')
                                if active_sess:
                                    active_sess = active_sess[0]
                                else:
                                    # Otherwise, generate a new session
                                    session_type = Session_Type.objects.get(name='phone')
                                    active_sess = generate_session(user, session_type)
                                    
                                json_data['session_id'] = active_sess.session_id
                                
                                # Update the date_last_session_access for the user (this drives reminder emails)
                                date_access = datetime.datetime.now()
                                Subject.objects.filter(user_id=user.user_id).update(date_last_session_access=date_access)
                                
                                # Get all the unanswered tasks for the active session
                                active_tasks = Session_Task.objects.filter(session=active_sess,date_completed__isnull=True)
                                json_tasks = []
                                for task in active_tasks:
                                    active_task_instances = Session_Task_Instance.objects.filter(session_task=task)
                                    json_task_instances = []
                                    for instance in active_task_instances:
                                        response = Session_Response.objects.get(session_task_instance=instance)
                                        json_values = []
                                        active_instance_values = Session_Task_Instance_Value.objects.filter(session_task_instance=instance)
                                        for val in active_instance_values:
                                            value_text = val.value
                                            if val.value_display:
                                                value_text = val.value_display
                                                
                                            json_values += [ {'value_id': val.session_task_instance_value_id, \
                                                              'value_text': value_text, \
                                                              'value_type': val.task_field.field_type.name } ] 
                                        
                                        json_task_instances += [ {'session_task_instance_id': instance.session_task_instance_id, \
                                                                  'response_id': response.session_response_id, \
                                                                  'values': json_values } ]
                                        
                                    json_tasks += [ { 'session_task_id': task.session_task_id, \
                                                      'task_id': task.task_id, \
                                                      'order': task.order, \
                                                      'total_time': task.total_time, \
                                                      'session_task_instances': json_task_instances } ]
                                    
                                json_data['session_tasks'] = json_tasks
                                
                            else:
                                # The user birth date information that was passed in is incorrect, or 
                                # the user hasn't completed the demographics page yet
                                json_data['status'] = "error"
                                json_data['error'] = "Invalid user"
                                return HttpResponse(json.dumps(json_data))
                            
                        else:
                            # The user birth date information that was passed in is invalid
                            json_data['status'] = "error"
                            json_data['error'] = "Invalid user"
                            return HttpResponse(json.dumps(json_data))
                            
                    else:
                        # The 'user_passcode' (i.e., numeric user ID) is invalid / does not exist in subjects table
                        json_data['status'] = "error"
                        json_data['error'] = "Invalid user"
                        return HttpResponse(json.dumps(json_data))
                else:
                    # The 'user_passcode' (i.e., numeric user ID) was not specified, or the user birth date was not specified
                    json_data['status'] = "error"
                    json_data['error'] = "Invalid user"
                    return HttpResponse(json.dumps(json_data))
    else:
        json_data['status'] = "error"
        json_data['error'] = "Authentication error"
        return HttpResponse(json.dumps(json_data))
    
        
    return HttpResponse(json.dumps(json_data))
    