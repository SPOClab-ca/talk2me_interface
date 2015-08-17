import datetime
import os
import requests

def generate_log(r):
    return "\n".join([ "HTTP Response Status: %d (%s)" % (r.status_code, r.reason), \
                       "HTTP Response JSON: ", \
                       "\n".join([k + "=" + v for (k,v) in r.json().iteritems()]) \
                       ])

    
# Send out the reminders, and log the HTTP response from the server
r = requests.post("https://www.cs.toronto.edu/talk2me/maintenance/mailer/reminders", \
                  data={'auth_name': 'system', \
                        'auth_pass': 'test'})

# 14a90af63c607ba3c1ff3906f9f5150b61eae1cc56654ef2595b7491c633619f156a8b08f1ae3798413e1bff17bf6a01f0cf1ae9417f8bfab2bce120e0fac5ba                        
# Log the result
date_format = '%Y%m%d_%H%M%S'
timestamp = datetime.datetime.now().strftime(date_format)
base_dir = os.sep.join(['..', '..', 'csc2518_logs', 'reminders'])
log_file = os.path.join(base_dir, timestamp + '.log')

with open(log_file, 'w') as fout:
    fout.write(generate_log(r))

