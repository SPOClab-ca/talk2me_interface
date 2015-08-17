import datetime
import os
import requests

from settings import SYSTEM_CRED

def generate_log(r):
    return "\n".join([ "HTTP Response Status: %d (%s)" % (r.status_code, r.reason), \
                       "HTTP Response JSON: ", \
                       "\n".join([k + "=" + v for (k,v) in r.json().iteritems()]) \
                       ])

    
# Send out the reminders, and log the HTTP response from the server
r = requests.post("https://www.cs.toronto.edu/talk2me/maintenance/mailer/reminders", \
                  data={'auth_name': 'system', \
                        'auth_pass': SYSTEM_CRED})
                        
# Log the result
date_format = '%Y%m%d_%H%M%S'
timestamp = datetime.datetime.now().strftime(date_format)
base_dir = os.sep.join(['..', '..', 'csc2518_logs', 'reminders'])
log_file = os.path.join(base_dir, timestamp + '.log')

with open(log_file, 'w') as fout:
    fout.write(generate_log(r))

