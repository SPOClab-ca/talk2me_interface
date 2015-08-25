from django.template.loader import get_template
from django.template import TemplateDoesNotExist, Context
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotModified
from django.core.cache import cache
from django.conf import settings

from datetime import datetime
import json
import subprocess
import os

from csc2518.settings import SUBSITE_ID
from datacollector.models import *

global website_root
website_root = '/'
if SUBSITE_ID: website_root += SUBSITE_ID

# Generate a personalized certificate of completion of the study
def certificate(request, subject_id):
    
    json_data = {}
    json_data['status'] = 'success'
    
    # Verify user is valid
    s = Subject.objects.filter(user_id=subject_id)
    if s:
        s = s[0]
        u = User.objects.get(id=subject_id)
        
        # Ensure that the subject has at least one completed session
        sess = Session.objects.filter(subject=s, end_date__isnull=False)
        if sess:

            try:
		# Locate the template for the pdf
		template = "datacollector/certificate.tex"
		doc = template.rsplit('/', 1)[-1].rsplit('.', 1)[0]
		
		# Set up the personalized details (name of user and today's date)
		date_format_cert = '%d %B %Y'
		now = datetime.now()
		datestamp = now.strftime(date_format_cert)
		ctx = { "username": u.username, "datestamp": datestamp }
		
		# Define directories to be used. Current directory is where this script is located.
		date_format = '%Y%m%d_%H%M%S'
		current_dir = os.path.abspath(os.path.dirname(__file__))
		img_dir = os.path.join(current_dir, os.sep.join(["static", "img"]))
		template_dir = os.path.join(os.path.join(current_dir, os.pardir), os.sep.join(["templates", "datacollector"]))
		output_dir = os.path.join(current_dir, os.sep.join(["prizes"]))
		output_file = "%s_%s" % (u.username, now.strftime(date_format))

		# Fill out the template with the personalized details
		body = get_template(template).render(Context(ctx)).encode("utf-8")
		if '\\nonstopmode' not in body:
		    raise ValueError("\\nonstopmode not present in document, cowardly refusing to process.")
		
		# Create a temporary file for storing the personalized latex file during creation
		tmp_file = os.path.join(template_dir, output_file) + ".tex"
		with open(tmp_file, "w") as f:
		    f.write(body)
		
		# Generate the pdf! Have to run three times in order to render all borders correctly.
		for i in range(3):
		    p = subprocess.call(["pdflatex", "-output-directory", output_dir, tmp_file], cwd=img_dir)
		
		# Clean up temp file
		os.remove(tmp_file)
		
		# Return the newly generated file to the user
		#pdf = open(os.path.join(output_dir, output_file) + ".pdf")
		#res = HttpResponse(pdf, mimetype="application/pdf")
		#return res
		
		# Redirect to a page that displays the pdf to the user
		return HttpResponse(json.dumps(json_data))
            except:
                return HttpResponseRedirect(website_root + 'error/501')
        else:
            json_data['status'] = 'error'
            json_data['error'] = 'Unauthorized: you have not fully completed any sessions.'
            return HttpResponse(json.dumps(json_data), status=401)
    else:
        json_data['status'] = 'error'
        json_data['error'] = 'Unauthorized'
        return HttpResponse(json.dumps(json_data), status=401)
    
    
