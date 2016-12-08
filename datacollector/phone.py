# Create views handling phone API

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from datacollector.views import generate_session
from datacollector.models import *
from csc2518.settings import MEDIA_ROOT

import bcrypt
import crypto
import datetime
import json
import lib
import os


@csrf_exempt
def status(request):
	return HttpResponse(json.dumps({"status_code": "200"}))

@csrf_exempt
def login(request):
    if request.method == "POST" and request.body:
        request_json = json.loads(request.body)		
        if 'subject_id' in request_json and 'password' in request_json and 'grant_type' in request_json and \
            'client_id' in request_json and 'client_secret' in request_json:
            subject_id = request_json['subject_id']
            password = request_json['password']
            grant_type = request_json['grant_type']
            client_id = request_json['client_id']
            client_secret = request_json['client_secret']

            # Only the Resource Owner Password grant is implemented (the client
            # is always trusted).
            if not grant_type or grant_type != 'password':
                return HttpResponse(status=400, content=json.dumps({"status_code": "400", "error": "unsupported_grant_type"}))
            
            # Unicode objects need to be encoded before hashing them (otherwise 
            # bcrypt raises an error). Flask returns POST values in unicode.
            password = password.encode('utf-8')
            client_secret = client_secret.encode('utf-8')

            # First, authenticate the client.
            row_vals = Client.objects.filter(client_id=client_id)
            if len(row_vals) == 1:
                hashed_secret, secret_expirydate = row_vals[0].secret, row_vals[0].secret_expirydate
                hashed_secret = hashed_secret.encode('utf-8')
                #test = bcrypt.hashpw(client_secret + crypto.HASH_PEPPER, hashed_secret)
                #return HttpResponse(status=200, content=json.dumps({"status_code": "200", "hashed_secret": hashed_secret, "secret_expirydate": secret_expirydate, "test": test}))
                if (secret_expirydate is not None and secret_expirydate < datetime.datetime.now()) or bcrypt.hashpw(client_secret + crypto.HASH_PEPPER, hashed_secret) != hashed_secret:
                    # The secrets do not match OR the secret is expired, raise an exception
                    return HttpResponse(status=400, content=json.dumps({"status_code": "400", "error": "unauthorized_client"}))
            else:
                return HttpResponse(status=400, content=json.dumps({"status_code": "400", "error": "invalid_client"}))
            
            # Compare the received password (with salt and pepper) and hashed 
            # using bcrypt, to the hashed password in the database.
            # NB: bcrypt encodes the salt in the hashed password.
            if subject_id and str(subject_id).isdigit():
                try:
                    username = User.objects.get(id=subject_id).username
                except:
                    # Subject ID doesn't exist
                    return HttpResponse(status=400, content=json.dumps({"status_code": "400", "error": "invalid_grant"}))
            
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                # Log the user in
                auth_login(request, user)

                # Generate an access token for the session
                subject = Subject.objects.get(user_id=user.id)
                new_auth_token = crypto.generate_confirmation_token(username)
                new_auth_token_expirydate = datetime.datetime.now() + datetime.timedelta(days=1)
                expires_in = (new_auth_token_expirydate - datetime.datetime.now()).total_seconds()
                
                subject.auth_token = new_auth_token
                subject.auth_token_expirydate = new_auth_token_expirydate
                subject.save()
                return HttpResponse(status=200, content=json.dumps({"status_code": "200", "access_token": new_auth_token, \
                        "expires_in": expires_in, "token_type": "bearer"}))
            else:
                # Either the user doesn't exist, the password is incorrect, or the account has been deactivated
                return HttpResponse(status=400, content=json.dumps({"status_code": "400", "error": "invalid_grant"}))
            
    return HttpResponse(status=404, content=json.dumps({"status_code": "404", "error": "Not Found"}))

@csrf_exempt
def session(request):
    # Validate the headers
    auth_token = lib.validate_authorization_header(request.META)
    if not auth_token:
        response = HttpResponse(status=400, \
            content=json.dumps({"status_code": "400"}))
        response['WWW-Authenticate'] = 'Bearer error="invalid_request"' 
        return response
    
    # Validate the access token
    subject = lib.authenticate(auth_token)
    if not subject:
        response = HttpResponse(status=401, \
            content=json.dumps({"status_code": "401"}))
        response['WWW-Authenticate'] = 'Bearer error="invalid_token"'
        return response

    if request.method == 'GET':
        # Return all active sessions for the authenticated user

                # Get a list of all active sessions
        sessions = Session.objects.filter(subject=subject)
        list_sessions = []
        date_format = "%Y-%m-%d %H:%M:%S"
        for session in sessions:
            str_startdate = session.start_date.strftime(date_format)
            str_enddate = session.end_date
            if str_enddate is not None:
                str_enddate = str_enddate.strftime(date_format)
            list_sessions += [{"session_id": session.session_id, "start_date": str_startdate, "end_date": str_enddate, "session_type": session.session_type.name}]
        return HttpResponse(status=200, content=json.dumps({"status_code": "200", "sessions": list_sessions}))
        
    elif request.method == 'POST':
        # Create a new session for the user
        session_type = Session_Type.objects.get(name='phone')
        new_session = generate_session(subject, session_type)
        return HttpResponse(status=200, content=json.dumps({"status_code": "200", "session_id": new_session.session_id}))
 
    return HttpResponse(status=405, content=json.dumps({"status_code": "405", "error": "Invalid method"}))

@csrf_exempt
def session_tasklist(request, session_id):
    # Validate the headers
    auth_token = lib.validate_authorization_header(request.META)
    if not auth_token:
        response = HttpResponse(status=400, \
            content=json.dumps({"status_code": "400"}))
        response['WWW-Authenticate'] = 'Bearer error="invalid_request"' 
        return response
    
    # Validate the access token
    subject = lib.authenticate(auth_token)
    if not subject:
        response = HttpResponse(status=401, \
            content=json.dumps({"status_code": "401"}))
        response['WWW-Authenticate'] = 'Bearer error="invalid_token"'
        return response

    if request.method == 'GET':
        # Return all tasks for the requested session ID IFF the session belongs to the authenticated user
        session = Session.objects.filter(subject=subject, session_id=session_id)
        if session:
            session = session[0] 
            session_tasks = Session_Task.objects.filter(session=session)
            list_session_tasks = []
            date_format = "%Y-%m-%d %H:%M:%S"
            for session_task in session_tasks:
                str_datecompleted = session_task.date_completed
                if str_datecompleted is not None:
                    str_datecompleted = str_datecompleted.strftime(date_format)
                list_session_tasks += [{"session_task_id": session_task.session_task_id, "task_name": session_task.task.name_id, "order": session_task.order, "date_completed": str_datecompleted}]
            return HttpResponse(status=200, content=json.dumps({"status_code": "200", "session_tasks": list_session_tasks}))
            
        return HttpResponse(status=404, content=json.dumps({"status_code": "404", "error": "Not Found"}))
    return HttpResponse(status=405, content=json.dumps({"status_code": "405", "error": "Invalid method"}))

@csrf_exempt
def session_task(request, session_task_id):
    # Validate the headers
    auth_token = lib.validate_authorization_header(request.META)
    if not auth_token:
        response = HttpResponse(status=400, \
            content=json.dumps({"status_code": "400"}))
        response['WWW-Authenticate'] = 'Bearer error="invalid_request"' 
        return response
    
    # Validate the access token
    subject = lib.authenticate(auth_token)
    if not subject:
        response = HttpResponse(status=401, \
            content=json.dumps({"status_code": "401"}))
        response['WWW-Authenticate'] = 'Bearer error="invalid_token"'
        return response

    if request.method == 'GET':
        # Return all tasks for the requested session ID IFF the session belongs to the authenticated user
        session_task = Session_Task.objects.filter(session_task_id=session_task_id, session__subject=subject)
        if session_task:
            session_task = session_task[0] 
            list_session_task_instances = []
            date_format = "%Y-%m-%d %H:%M:%S"
            session_task_instance_values = Session_Task_Instance_Value.objects.filter(session_task_instance__session_task=session_task, task_field__field_type__name='display').order_by('session_task_instance', 'task_field')
            for session_task_instance_value in session_task_instance_values:
                str_datecompleted = None
                session_response = Session_Response.objects.filter(session_task_instance_id=session_task_instance_value.session_task_instance_id)
                if session_response:
                    session_response = session_response[0]
                    str_datecompleted = session_response.date_completed
                    if str_datecompleted is not None:
                        str_datecompleted = str_datecompleted.strftime(date_format)
                list_session_task_instances += [{"session_task_instance_id": session_task_instance_value.session_task_instance_id, "value": session_task_instance_value.value, "value_display": session_task_instance_value.value_display, "difficulty_id": session_task_instance_value.difficulty_id, "date_completed": str_datecompleted}]
            return HttpResponse(status=200, content=json.dumps({"status_code": "200", "session_task_instances": list_session_task_instances}))
            
        return HttpResponse(status=404, content=json.dumps({"status_code": "404", "error": "Not Found"}))
    return HttpResponse(status=405, content=json.dumps({"status_code": "405", "error": "Invalid method"}))

@csrf_exempt
def response(request):
    # Validate the headers
    auth_token = lib.validate_authorization_header(request.META)
    if not auth_token:
        response = HttpResponse(status=400, \
            content=json.dumps({"status_code": "400"}))
        response['WWW-Authenticate'] = 'Bearer error="invalid_request"' 
        return response
    
    # Validate the access token
    subject = lib.authenticate(auth_token)
    if not subject:
        response = HttpResponse(status=401, \
            content=json.dumps({"status_code": "401"}))
        response['WWW-Authenticate'] = 'Bearer error="invalid_token"'
        return response

    if request.method == 'POST':
        if request.POST and 'session_task_instance_id' in request.POST and 'date_responded' in request.POST and request.FILES and 'audio' in request.FILES:
            session_task_instance_id = request.POST['session_task_instance_id']
            date_responded = request.POST['date_responded']
            audio_data = ContentFile(request.FILES['audio'].read())
            
            # Check that the task instance ID is valid and that the response hasn't been submitted before
            session_response = Session_Response.objects.filter(session_task_instance_id=session_task_instance_id, date_completed__isnull=True)
            if session_response:
                session_response = session_response[0]

                # Save the audio response and update the db record
                session_response.value_audio.save('', audio_data)
                session_response.date_completed = date_responded
                session_response.save()

                # Compute a checksum for the file stored on the server
                filepath = os.path.join(MEDIA_ROOT, session_response.value_audio.name)
                file_checksum = lib.generate_md5_checksum(filepath)

                return HttpResponse(status=200, content=json.dumps({"status_code": "200", "file_checksum": file_checksum}))
        return HttpResponse(status=404, content=json.dumps({"status_code": "404", "error": "Not Found"}))
    return HttpResponse(status=405, content=json.dumps({"status_code": "405", "error": "Invalid method"}))

@csrf_exempt
def old_session(request):
    json_data = {}
    json_data['status'] = "200"
    
    # Respond to a preflight OPTIONS request from external (CORS) requestor, by adding the necessary response headers
    if request.method == "OPTIONS":
        response = HttpResponse(json.dumps(json_data))
        response["Content-type"] = "application/json"
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST"
        response["Access-Control-Allow-Headers"] = "Accept, Content-Type, X-CSRFToken, X-Requested-With"
        return response
    
    elif request.method == "POST":
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
                        if user is not None and user:
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
                                    json_task_instances = []
                                    active_responses = Session_Response.objects.filter(session_task_instance__session_task__session=active_sess, date_completed__isnull=True)
                                    for response in active_responses:
                                        json_values = []
                                        active_instance_values = Session_Task_Instance_Value.objects.filter(session_task_instance=response.session_task_instance)
                                        for val in active_instance_values:
                                            value_text = val.value
                                            if val.value_display:
                                                value_text = val.value_display
                                            json_values += [ {'value_id': val.session_task_instance_value_id, \
                                                              'value_text': value_text, \
                                                              'value_type': val.task_field.field_type.name } ] 
                                        
                                        json_task_instances += [ { 'task_id': response.session_task_instance.session_task.task_id, \
                                                                   'task_name': response.session_task_instance.session_task.task.name, \
                                                                   'task_instruction': response.session_task_instance.session_task.task.instruction_phone, \
                                                                   'session_task_id': response.session_task_instance.session_task_id, \
                                                                   'order': response.session_task_instance.session_task.order, \
                                                                   'total_time': response.session_task_instance.session_task.total_time, \
                                                                   'session_task_instance_id': response.session_task_instance_id, \
                                                                   'response_id': response.session_response_id, \
                                                                   'values': json_values } ]
                                    json_data['session_task_instances'] = json_task_instances
                                    
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
            return HttpResponse("Unauthorized", status=401)
        
        response = HttpResponse(json.dumps(json_data))
        response["Content-type"] = "application/json"
        response["Access-Control-Allow-Origin"] = "*"
        return response
    
    # If the request is not OPTIONS or POST, just return 401
    return HttpResponse("Unauthorized", status=401)
