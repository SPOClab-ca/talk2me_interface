from datacollector.models import *
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import calendar
import datetime
import emails
import json
import numpy as np
from numpy.random import random_sample


# Set up mail authentication
global email_username, email_password, email_name, website_hostname, reminder_freq, date_format
email_username = Settings.objects.get(setting_name="system_email").setting_value
email_name = Settings.objects.get(setting_name="system_email_name").setting_value
website_hostname = Settings.objects.get(setting_name="website_hostname").setting_value
website_name = Settings.objects.get(setting_name="website_name").setting_value

today = datetime.datetime.now().date()
reminder_freq = { 7: "Weekly", 30: "Monthly", 365: "Annual" }
date_format = "%Y-%m-%d"


@csrf_exempt
def reminders(request):
    json_data = {}
    json_data['status'] = "success"
    email_type = 'reminder'
    
    # Authenticate the request - has to be issued by a superuser
    if 'auth_name' in request.POST and 'auth_pass' in request.POST:
        username = request.POST['auth_name']
        password = request.POST['auth_pass']
        system_user = authenticate(username=username, password=password)
        output = ""
        if system_user is not None:
            if system_user.is_active and system_user.is_superuser:
                
                # Find all users who we need to remind & who have a validated email address
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
                        # should be sent, and if it is, check if a reminder email was already sent
                        # today (to avoid duplication, e.g. if the script is re-run twice on same day)
                        delta = (today - date_first_reminder).days
                        if delta >= 0:
                            if delta % user_pref_freq == 0:
                                # Time for a reminder, but check if one was already sent today
                                existing_reminders = Subject_Emails.objects.filter(date_sent=today, subject=user, email_to=user_email, email_type=email_type)
                                if not existing_reminders:
                                    output += ", Time for a reminder (last access date: %s, reminder freq in days: %s)" % (date_last_access, user_pref_freq)
                                    
                                    # Set up message
                                    email_subject = "%s - %s Reminder" % (website_name, reminder_freq[user_pref_freq])
                                    email_sender = email_username
                                    email_receiver = user_email
                                    email_text = "Dear <b>%s</b>, \r\n\r\nIt's time for your next session on %s! When you are ready for some new language puzzles, <a href='%s'>click here</a>. Your participation in this project is important to us, and directly helps enable research into language pattern changes over time.\r\n\r\n- The SPOClab team!\r\n\r\nSPOClab: Signal Processing and Oral Communication lab\r\n550 University Avenue, 12-175\r\nToronto, Ontario M5G 2A2\r\n<a href='http://spoclab.ca'>http://spoclab.ca</a>\r\n\r\nYou are receiving this email due to your account preferences. To unsubscribe, please visit <a href='%s'>your Account Settings page</a>." % (username, website_name, website_hostname, website_hostname + '/account')
                                    email_html = """<h2 style="Margin-top: 0;color: #44a8c7;font-weight: 700;font-size: 24px;Margin-bottom: 16px;font-family: Lato,sans-serif;line-height: 32px;text-align: center">Dear %s, it's time for your next session on %s!</h2>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">When you are ready for some new language puzzles,\r\n <a style="text-decoration: none;color: #5c91ad;border-bottom: 1px dotted #5c91ad" data-emb-href-display="undefined" href='%s'>click here</a>.\r\n Your participation in this project is important to us, and directly helps enable research into language pattern changes over time.</p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">&mdash; The SPOClab team</p>""" % (username, website_name, website_hostname)
                                    
                                    output += ", Message from %s (%s) to %s, body: %s" % (email_sender, email_subject, email_receiver, email_text)
                                    
                                    # Send the prepared email
                                    result_flag = emails.sendEmail(email_sender, email_name, [email_receiver], [], [], email_subject, email_text, emails.emailPre + email_html + emails.emailPost)
                                    
                                    # If the send was successful, record it in the database
                                    if result_flag:
                                        Subject_Emails.objects.create(date_sent=today, subject=user, email_from=email_sender, email_to=email_receiver, email_type=email_type)
            else:
                json_data['status'] = 'error'
                json_data['error'] = 'Unauthorized'
                return HttpResponse(json.dumps(json_data), status=401)
        else:
            json_data['status'] = 'error'
            json_data['error'] = 'Unauthorized'
            return HttpResponse(json.dumps(json_data), status=401)
        
        #json_data['debug'] = output
        return HttpResponse(json.dumps(json_data))
    else:
        json_data['status'] = 'error'
        json_data['error'] = 'Unauthorized'
        return HttpResponse(json.dumps(json_data), status=401)


@csrf_exempt
def monthlydraw(request):
    json_data = {}
    json_data['status'] = "success"
    email_type = 'prize_notification'
    notification_type = Notification.objects.get(notification_id='monthlyprize_winner')
    NUM_WINNERS = 5
    
    # Authenticate the request - has to be issued by a superuser
    if 'auth_name' in request.POST and 'auth_pass' in request.POST:
        username = request.POST['auth_name']
        password = request.POST['auth_pass']
        system_user = authenticate(username=username, password=password)
        output = ""
        if system_user is not None:
            if system_user.is_active and system_user.is_superuser:
            
                today = datetime.datetime.now().date()
                month_start = datetime.date(today.year, today.month, 1)
                month_end = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
                
                # Build a list of all available prizes
                prizes_list = [p.prize_name for p in Prize.objects.filter(prize_value__gt=0).order_by('prize_name')]
                
                # Build a probability distribution over the users who have
                # at least one completed session over the past month, and have elected
                # to participate in the monthly prize draws, and have a valid email 
                # address. 
                # The probability of winning is equal to the number of completed sessions over the 
                # past month / total number of completed sessions over the past month.
                # NB: it doesn't matter when the session was started.
                subj_eligible = Subject.objects.filter(preference_prizes=1, email_prizes__isnull=False, email_validated=1, session__isnull=False, session__end_date__isnull=False, session__end_date__gte=month_start, session__end_date__lte=month_end).distinct().annotate(Count('session'))
                total_sess = sum([x.session__count for x in subj_eligible])
                
                distribution_values = np.array([x.user_id for x in subj_eligible])
                distribution_prob = np.array([x.session__count * 1.0 / total_sess for x in subj_eligible])
                
                # The number of winners is either the pre-specified number, or the number of eligible subjects
                # (if the latter is smaller).
                NUM_WINNERS = min(NUM_WINNERS, len(subj_eligible))
                
                # Select the winners randomly by sampling the distribution, without replacement.
                winners = []
                for run in range(NUM_WINNERS):
                    bins = np.add.accumulate(distribution_prob)
                    winner_ind = np.digitize(random_sample(1), bins)
                    winner_id = int(distribution_values[winner_ind])
                    winner_subject = Subject.objects.get(user_id=winner_id)
                    winner_user = User.objects.get(id=winner_id)
                    winners += [winner_id]
                    
                    # Update the distribution (remove the winner that was just selected).
                    distribution_values = np.delete(distribution_values, winner_ind)
                    distribution_prob = np.delete(distribution_prob, winner_ind)
                    normalization_factor = sum(distribution_prob)
                    distribution_prob = np.divide(distribution_prob, normalization_factor)
                    
                    # 1) Send an email to the winner
                    email_subject = "%s - Monthly Prize Winner" % (website_name)
                    email_sender = email_username
                    email_receiver = winner_user.email
                    email_text = "Dear <b>%s</b>, \r\n\r\nYou won a prize from the monthly draw on %s!\r\n\r\nTo claim your prize, please respond to this email with the following information:\r\n\r\n1. Your e-mail address where you would like to receive the prize\r\n2. Your choice of prize (choose ONE of the following):\r\n%s\r\n\r\nThank you for your participation this month. You're awesome!\r\n\r\n- The SPOClab team!\r\n\r\nSPOClab: Signal Processing and Oral Communication lab\r\n550 University Avenue, 12-175\r\nToronto, Ontario M5G 2A2\r\n<a href='http://spoclab.ca'>http://spoclab.ca</a>\r\n\r\nYou are receiving this email due to your account preferences. To unsubscribe, please visit <a href='%s'>your Account Settings page</a>." % (winner_user.username, website_name, "\r\n".join(prizes_list), website_hostname + '/account')
                    email_html = """<h2 style="Margin-top: 0;color: #44a8c7;font-weight: 700;font-size: 24px;Margin-bottom: 16px;font-family: Lato,sans-serif;line-height: 32px;text-align: center">Dear %s, you won a prize from the monthly draw on %s!</h2>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">To claim your prize, please respond to this email with the following information:\r\n<ol style="font-size: 15px;font-family: sans-serif;line-height: 24px;text-align: left; margin-bottom: 24px;color: #000000;">\r\n<li>Your e-mail address where you would like to receive the prize</li>\r\n<li>Your choice of prize (choose ONE of the following):<br />%s</li></ol></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">&mdash; The SPOClab team</p>""" % (winner_user.username, website_name, "<br />\r\n".join(prizes_list))
                    
                    result_flag = emails.sendEmail(email_sender, email_name, [email_receiver], [], [], email_subject, email_text, emails.emailPre + email_html + emails.emailPost)
                    
                    # If the send was successful, record it in the database
                    if result_flag:
                        Subject_Emails.objects.create(date_sent=today, subject=winner_subject, email_from=email_sender, email_to=email_receiver, email_type=email_type)
                    
                    # 2) Issue a notification to the winner (to be seen within the website). There is no expiry/end date for prizes.
                    Subject_Notifications.objects.create(subject=winner_subject, notification=notification_type, date_start=today, dismissed=0)
                    
                json_data['winners'] = " || ".join([str(w) for w in winners])
                
    return HttpResponse(json.dumps(json_data))
    
