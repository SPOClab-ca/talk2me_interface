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

email_username = Settings.objects.get(setting_name="system_email").setting_value
website_name = Settings.objects.get(setting_name="website_name").setting_value

global website_root, global_passed_vars
global_passed_vars = { "website_id": "talk2me", "website_name": website_name, "website_email": email_username }
website_root = '/'
if SUBSITE_ID: website_root += SUBSITE_ID


# Display a PDF certificate
def certificate(request):
    
    if request.user.is_authenticated():
        # Verify user is valid
        s = Subject.objects.filter(user_id=request.user.id)
        if s:
            s = s[0]
            
            # Check if the certificate has been generated before. If yes, simply display it. 
            # If not, generate it now.
            cert = Subject_Prizes.objects.filter(subject=s, prize__prize_id="certificate_participation")
            if not cert:
                # Ensure that the subject has at least one completed session
                sess = Session.objects.filter(subject=s, end_date__isnull=False)
                if sess:
                    cert = gen_certificate(request.user)
            else:
                cert = cert[0]
                
            if cert:
                current_dir = os.path.abspath(os.path.dirname(__file__))
                cert_filename = os.path.join(current_dir, os.sep.join(["prizes", cert.filename]))
                with open(cert_filename, "rb") as pdf:
                    response = HttpResponse(pdf.read(), content_type="application/pdf")
                    response['Content-Disposition'] = 'filename="' + global_passed_vars['website_id'] + '_certificate.pdf"'
                    return response
            
    # The user is not authenticated, or there was an error that occurred
    return HttpResponseRedirect(website_root)
    
    
# Helper function.
# Generate a personalized certificate of completion of the study, and record it in the db.
def gen_certificate(user):

    try:
        s = Subject.objects.get(user_id=user.id)
        
        # Locate the template for the pdf
        template = "datacollector/certificate.tex"
        doc = template.rsplit('/', 1)[-1].rsplit('.', 1)[0]
        
        # Set up the personalized details (name of user and today's date).
        # Escape the username for underscore, since latex can't process them unescaped.
        date_format_cert = '%d %B %Y'
        now = datetime.now()
        datestamp = now.strftime(date_format_cert)
        ctx = { "username": user.username.replace("_", "\_"), "datestamp": datestamp }
        
        # Define directories to be used. Current directory is where this script is located.
        date_format = '%Y%m%d_%H%M%S'
        current_dir = os.path.abspath(os.path.dirname(__file__))
        img_dir = os.path.join(current_dir, os.sep.join(["static", "img"]))
        template_dir = os.path.join(os.path.join(current_dir, os.pardir), os.sep.join(["templates", "datacollector"]))
        output_dir = os.path.join(current_dir, os.sep.join(["prizes"]))
        output_file = "%s_%s" % (str(user.id), now.strftime(date_format))

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
        
        # Record the filename in the db
        prize_cert = Prize.objects.get(prize_id="certificate_participation")
        new_cert = Subject_Prizes.objects.create(subject=s, prize=prize_cert, date_received=now, filename="%s.pdf" % output_file)
        return new_cert
    except:
        return None
            
