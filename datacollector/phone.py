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
    if 'auth_name' in request.GET and 'auth_pass' in request.GET:
        username = request.GET['auth_name']
        password = request.GET['auth_pass']
        system_user = authenticate(username=username, password=password)
        if system_user is not None:
            if system_user.is_active and system_user.is_superuser:
                # If the user is a valid superuser, 
                # proceed with returning the active phone session for the requested user (if one exists),
                # or create a new session (if none exist).
                if 'user_passcode' in request.GET:
                    # Validate user
                    user = Subject.objects.filter(user_id=request.GET['user_passcode'])
                    if user is not None:
                        user = user[0]
                        
                        # Look for latest active session, if one exists
                        active_sess = Session.objects.filter(subject=user).order_by('-session_id')
                        if active_sess:
                            active_sess = active_sess[0]
                        else:
                            # Otherwise, generate a new session
                            active_sess = generate_session(user)
                            
                        json_data['session_id'] = active_sess.session_id
                        
                        # Update the date_last_session_access for the user (this drives reminder emails)
                        date_access = datetime.datetime.now()
                        Subject.objects.filter(user_id=user.user_id).update(date_last_session_access=date_access)
                        
                        
                            
                    else:
                        # The 'user_passcode' (i.e., numeric user ID) is invalid / does not exist in subjects table
                        json_data['status'] = "error"
                        json_data['error'] = "Invalid user"
                        return HttpResponse(json.dumps(json_data))
                else:
                    # The 'user_passcode' (i.e., numeric user ID) was not specified
                    json_data['status'] = "error"
                    json_data['error'] = "Invalid user"
                    return HttpResponse(json.dumps(json_data))
    else:
        json_data['status'] = "error"
        json_data['error'] = "Authentication error"
        return HttpResponse(json.dumps(json_data))
    
        
    return HttpResponse(json.dumps(json_data))
    