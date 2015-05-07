from datacollector.models import *
import datetime
import smtplib


# Set up mail authentication
global email_username, email_password, website_hostname, reminder_freq, date_format
email_username = Settings.objects.get(name="system_email")
email_password = Settings.objects.get(name="system_email_passwd")
website_hostname = Settings.objects.get(name="website_hostname")

today = datetime.datetime.now()
reminder_freq = { 7: "Weekly", 30: "Monthly", 365: "Annual" }
date_format = "%Y-%m-%d"

def sendReminder(reminder_msg):
    
    # Send the message via Gmail's SMTP server
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(email_username, email_password)
    server.sendmail(email_sender, [email_receiver], reminder_msg)
    server.quit()


# Find all users whom we need to remind
users_to_remind = Subject.objects.filter(preference_email_reminders=1).exclude(email_reminders__isnull=True).exclude(preference_email_reminders_freq__isnull=True)
for user in users_to_remind:
    
    # Check if it has been X days since the last session access
    user_email = user.email_reminders
    user_pref_freq = int(user.preference_email_reminders_freq)
    user_last_access = user.date_last_session_access
    date_last_access = datetime.datetime.strptime(user_last_access, date_format)
    date_first_reminder = date_last_access + datetime.timedelta(days=user_pref_freq)
    delta = (today - date_first_reminder).days
    if delta >= 0:
        if delta % user_pref_freq == 0:
            # Time for a reminder
            
            
            # Set up message
            email_subject = "Talk2Me (University of Toronto) - %s Reminder"
            email_sender = email_username
            email_receiver = "talk2me.toronto@gmail.com"
            email_body = "Dear <b>%s</b>, \r\n\r\nIt's time for your next session on Talk2Me! When you are ready for some new language puzzles, <a href='" + website_hostname + "'>click here</a>. Your participation in this project is important to us, and directly helps enable important research into language pattern changes over time. "
            
            msg = "\r\n".join([
              "From: " + email_sender,
              "To: " + email_receiver,
              "Subject: " + email_subject,
              "",
              email_body
              ])
            