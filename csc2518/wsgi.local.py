# import os
# import sys

# # path = '/u/spoclabweb/site/csc2518'
# # if path not in sys.path:
# #     sys.path.append(path)

# #os.environ['DJANGO_SETTINGS_MODULE'] = 'csc2518.settings'

# import django
# #django.setup()

# import django.core.handlers.wsgi
# #application = django.core.handlers.wsgi.WSGIHandler()

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csc2518.settings")

# application = get_wsgi_application()


import os
import sys

#path = '/u/spoclabweb/site/csc2518'
path = '~/django_datacollector/csc2518'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'csc2518.settings'

import django
django.setup()

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()