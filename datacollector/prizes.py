from django.template.loader import get_template
from django.template import TemplateDoesNotExist, Context
from django.http import HttpResponse, Http404, HttpResponseNotModified
from django.core.cache import cache
from django.conf import settings

from datetime import datetime
import json
from tempfile import mkdtemp
import subprocess
import os
import shutil
from hashlib import md5

from datacollector.models import *


TEMP_PREFIX = getattr(settings, 'TEX_TEMP_PREFIX', 'talk2me_gencert-')
CACHE_PREFIX = getattr(settings, 'TEX_CACHE_PREFIX', 'talk2me-gencert')
CACHE_TIMEOUT = getattr(settings, 'TEX_CACHE_TIMEOUT', 86400)  # 1 day


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
            
            # Locate the template for the pdf
            template = "datacollector/certificate.tex"
            doc = template.rsplit('/', 1)[-1].rsplit('.', 1)[0]
            
            # Fill out the template with the personalized details (name of user and today's date)
            date_format_cert = '%d %B %Y'
            now = datetime.now()
            datestamp = now.strftime(date_format_cert)
            logofile = os.path.join(os.path.abspath(__file__), "static/img/uoft_logo_web.jpg")
            logofile = "uoft_logo_web.jpg"
            ctx = { "username": u.username, "datestamp": datestamp, "logofile": logofile }
            json_data['logofile'] = logofile
            
            # Store the generated pdf in the current directory
            date_format = '%Y%m%d_%H%M%S'
            output_dir = os.path.join(os.getcwd(), "datacollector" + os.sep + "prizes")
            output_file = "%s_%s" % (u.username, now.strftime(date_format))
            json_data['output_dir'] = output_dir
            
            try:
                body = get_template(template).render(Context(ctx)).encode("utf-8")
                json_data['txt'] = body
                
                etag = md5(body).hexdigest()
                if request.META.get('HTTP_IF_NONE_MATCH', '') == etag:
                    return HttpResponseNotModified()
                
                cache_key = "%s:%s:%s" % (CACHE_PREFIX, template, etag)
                pdf = cache.get(cache_key)
                if pdf is None:
                    # Generate the pdf!
                    if '\\nonstopmode' not in body:
                        raise ValueError("\\nonstopmode not present in document, cowardly refusing to process.")
    
                    
                    # Create a unique temporary directory for storing the pdf during creation
                    tmp = mkdtemp(prefix=TEMP_PREFIX)
                    tmp_file = os.path.join(tmp, output_file) + ".tex"
                    try:
                        with open(tmp_file, "w") as f:
                            f.write(body)
                            json_data['tmp_file'] = tmp_file
                        del body

                        error = subprocess.Popen( \
                            ["pdflatex", "%s.tex" % output_file, "-output-directory", output_dir], \
                            cwd=tmp, \
                            stdin=open(os.devnull, "r"), \
                            stderr=open(os.devnull, "wb"), \
                            stdout=open(os.devnull, "wb") \
                        ).wait()
                        
                        if error:
                            raise RuntimeError("pdflatex error (code %s) in %s/%s" % (error, tmp, doc))

                        pdf = open(os.path.join(output_dir, output_file) + ".pdf")
                        
                    except:
                        raise RuntimeError("PDF generation error. Please contact the website administrators.")
                    #finally:
                    #    shutil.rmtree(tmp)

                    if pdf:
                        cache.set(cache_key, pdf, CACHE_TIMEOUT)
                    
                #res = HttpResponse(pdf, mimetype="application/pdf")
                #res['ETag'] = etag
                #return res
                    
                return HttpResponse(json.dumps(json_data))
            except TemplateDoesNotExist:
                json_data['status'] = 'error'
                json_data['error'] = 'Template does not exist'
                return HttpResponse(json.dumps(json_data), status=401)
            
        else:
            json_data['status'] = 'error'
            json_data['error'] = 'Unauthorized: you have not fully completed any sessions.'
            return HttpResponse(json.dumps(json_data), status=401)
    else:
        json_data['status'] = 'error'
        json_data['error'] = 'Unauthorized'
        return HttpResponse(json.dumps(json_data), status=401)
    
    