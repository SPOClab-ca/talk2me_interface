from datacollector.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import datetime
import emails
import json


# Set up mail authentication
global email_username, email_password, email_name, website_hostname, reminder_freq, date_format
email_username = Settings.objects.get(setting_name="system_email").setting_value
email_name = Settings.objects.get(setting_name="system_email_name").setting_value
website_hostname = Settings.objects.get(setting_name="website_hostname").setting_value
website_name = "Talk2Me"

today = datetime.datetime.now().date()
reminder_freq = { 7: "Weekly", 30: "Monthly", 365: "Annual" }
date_format = "%Y-%m-%d"


@csrf_exempt
def reminders(request):
    json_data = {}
    json_data['status'] = "success"
    
    # Authenticate the request - has to be issued by a superuser
    if 'auth_name' in request.POST and 'auth_pass' in request.POST:
        username = request.POST['auth_name']
        password = request.POST['auth_pass']
        system_user = authenticate(username=username, password=password)
        output = ""
        if system_user is not None:
            if system_user.is_active and system_user.is_superuser:
                
                # Find all users whom we need to remind who have a validated email address
                users_to_remind = Subject.objects.filter(preference_email_reminders=1,email_validated=1,email_reminders__isnull=False,preference_email_reminders_freq__isnull=False)
                for user in users_to_remind:
                    
                    username = User.objects.get(id=user.user_id).username
                    output += "User to remind: %s, %s" % (user.user_id, username)
                    
                    # Check if it has been X days since the last session access
                    user_email = user.email_reminders
                    user_pref_freq = int(user.preference_email_reminders_freq)
                    user_last_access = user.date_last_session_access # stored as datetime.date
                    user_created = user.date_created # stored as datetime.date
                    
                    # Date of last access is either the last time the user accessed a session 
                    # OR the date they created their account (if they haven't created any 
                    # sessions yet)
                    date_last_access = None
                    if user_last_access:
                        date_last_access = user_last_access
                    elif user_created:
                        date_last_access = user_created
                    
                    if date_last_access:
                        # Compute the date when we need to send the first reminder: X days 
                        # (according to frequency preference) after the date of last access
                        date_first_reminder = date_last_access + datetime.timedelta(days=user_pref_freq)
                        
                        output += ", Date of first reminder: %s" % (date_first_reminder) 
                        
                        # Check if today's date is past the day when the first reminder 
                        # should be sent
                        delta = (today - date_first_reminder).days
                        if delta >= 0:
                            if delta % user_pref_freq == 0:
                                # Time for a reminder
                                output += ", Time for a reminder (last access date: %s, reminder freq in days: %s)" % (date_last_access, user_pref_freq)
                                
                                # Set up message
                                email_subject = "%s - %s Reminder" % (website_name, reminder_freq[user_pref_freq])
                                email_sender = email_username
                                email_receiver = user_email
                                email_text = "Dear <b>%s</b>, \r\n\r\nIt's time for your next session on %s! When you are ready for some new language puzzles, <a href='%s'>click here</a>. Your participation in this project is important to us, and directly helps enable research into language pattern changes over time.\r\n\r\n- The SPOClab team!\r\n\r\nSPOClab: Signal Processing and Oral Communication lab\r\n550 University Avenue, 12-175\r\nToronto, Ontario M5G 2A2\r\n<a href='http://spoclab.ca'>http://spoclab.ca</a>\r\n\r\nYou are receiving this email because you have chosen to receive session reminders. To unsubscribe, please visit <a href='%s'>your Account Settings page</a>." % (username, website_name, website_hostname, website_hostname + '/account')
                                email_html = """<h2 style="Margin-top: 0;color: #44a8c7;font-weight: 700;font-size: 24px;Margin-bottom: 16px;font-family: Tahoma,sans-serif;line-height: 32px;text-align: center">Dear %s, it's time for your next session on %s!</h2><p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">When you are ready for some new language puzzles, <a style="text-decoration: none;color: #5c91ad;border-bottom: 1px dotted #5c91ad" data-emb-href-display="undefined" href='%s'>click here</a>. Your participation in this project is important to us, and directly helps enable research into language pattern changes over time.</p><p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">&mdash; The SPOClab team</p>""" % (username, website_name, website_hostname)
                                
                                output += ", Message from %s (%s) to %s, body: %s" % (email_sender, email_subject, email_receiver, email_text)
                                
                                # Send the prepared email
                                result_flag = emails.sendEmail(email_sender, email_name, [email_receiver], [], [], email_subject, email_text, emails.emailPre + email_html + emails.emailPost)
                                
                                # If the send was successful, record it in the database
                                if result_flag:
                                    Subject_Emails.objects.create(date_sent=today, subject=user, email_from=email_sender, email_to=email_receiver, email_type='reminder')
                                
        json_data['debug'] = output
        return HttpResponse(json.dumps(json_data))
    else:
        json_data['status'] = 'error'
        json_data['error'] = 'Unauthorized'
        return HttpResponse(json.dumps(json_data), status=401)