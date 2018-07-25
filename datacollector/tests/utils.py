""" Helper functions used for testing. """

import datetime

from django.contrib.auth.models import User
from datacollector.models import Bundle, Session_Type, Subject, Subject_Bundle

TODAY = datetime.datetime.now().date()
#############################
####### GENERAL SETUP #######
#############################

def create_web_subject():
    ''' Create a generic Talk2Me web user.'''
    web_user = User.objects.create_user(username='web', email='@',
                                        password='web')
    web_subject = Subject.objects.create(user_id=web_user.id, date_created=TODAY)
    return web_subject

def create_web_user():
    ''' Create a generic Talk2Me web user.'''
    web_user = User.objects.create_user(username='web', email='@',
                                        password='web')
    Subject.objects.create(user_id=web_user.id, date_created=TODAY)
    return web_user

#############################
### BUNDLE-SPECIFIC SETUP ###
#############################

def create_uhn_web_bundle():
    ''' Create a UHN web bundle and return it.'''
    uhn_bundle = Bundle.objects.create(bundle_id=3, \
                                       name_id='uhn_web', \
                                       bundle_token='123qwert')
    return uhn_bundle

def create_uhn_phone_bundle():
    ''' Create a UHN phone bundle and return it.'''
    phone_bundle = Bundle.objects.create(bundle_id=4, \
                                         name_id='uhn_phone', \
                                         bundle_token='456qwert')
    return phone_bundle

def create_oise_bundle():
    ''' Create a OISE bundle and return it.'''
    oise_bundle = Bundle.objects.create(bundle_id=5, \
                                        name_id='oise', \
                                        bundle_token='123dklas')
    return oise_bundle

def create_wch_web_bundle():
    ''' Create a WCH web bundle and return it.'''
    wch_web_bundle = Bundle.objects.create(bundle_id=6, \
                                           name_id='wch_web', \
                                           bundle_token='456abc')
    return wch_web_bundle

def create_wch_phone_bundle():
    ''' Create a WCH web bundle and return it.'''
    wch_phone_bundle = Bundle.objects.create(bundle_id=7, name_id='wch_phone', bundle_token='123xyz')
    return wch_phone_bundle

def create_uhn_web_subject(uhn_bundle):
    ''' Create a UHN web user and subject and return the UHN web user.'''
    uhn_user = User.objects.create_user(username='uhn', email='@',
                                        password='uhn')
    uhn_subject = Subject.objects.create(user_id=uhn_user.id, date_created=TODAY)
    Subject_Bundle.objects.create(subject_bundle_id=1, subject_id=uhn_subject.user_id,
                                  bundle_id=uhn_bundle.bundle_id, active_startdate=TODAY)
    return uhn_subject

def create_wch_web_subject(wch_bundle):
    ''' Create a WCH web user and subject and return the WCH web user.'''
    wch_user = User.objects.create_user(username='wch_web',
                                        email='@',
                                        password='wch_web')
    wch_subject = Subject.objects.create(user_id=wch_user.id,
                                         date_created=TODAY)
    Subject_Bundle.objects.create(subject_bundle_id=3,
                                  subject_id=wch_subject.user_id,
                                  bundle_id=wch_bundle.bundle_id,
                                  active_startdate=TODAY)
    return wch_subject

def create_uhn_phone_subject(uhn_bundle):
    ''' Create a UHN phone user and subject and return the UHN phone user.'''
    uhn_user = User.objects.create_user(username='uhn_phone', email='@',
                                        password='uhn_phone')
    uhn_subject = Subject.objects.create(user_id=uhn_user.id, date_created=TODAY)
    Subject_Bundle.objects.create(subject_bundle_id=2, subject_id=uhn_subject.user_id,
                                  bundle_id=uhn_bundle.bundle_id, active_startdate=TODAY)
    return uhn_subject

def create_wch_phone_subject(wch_bundle):
    ''' Create a WCH phone user and subject and return the WCH phone user.'''
    wch_user = User.objects.create_user(username='wch_phone',
                                        email='@',
                                        password='wch_phone')
    wch_subject = Subject.objects.create(user_id=wch_user.id,
                                         date_created=TODAY)
    Subject_Bundle.objects.create(subject_bundle_id=4,
                                  subject_id=wch_subject.user_id,
                                  bundle_id=wch_bundle.bundle_id,
                                  active_startdate=TODAY)
    return wch_subject

def create_uhn_user(uhn_bundle):
    ''' Create a UHN user and subect and return the UHN subject.'''
    bundle_type = uhn_bundle.name_id
    uhn_user = User.objects.create_user(username=bundle_type, email='@',
                                        password=bundle_type)
    uhn_subject = Subject.objects.create(user_id=uhn_user.id, date_created=TODAY)
    Subject_Bundle.objects.create(subject_id=uhn_subject.user_id, bundle_id=uhn_bundle.bundle_id,
                                  active_startdate=TODAY)
    return uhn_user

def create_session_types():
    ''' Create the session types (website, phone).'''
    session_type_website = Session_Type.objects.create(session_type_id=1, name='website', text_only=0)
    session_type_phone = Session_Type.objects.create(session_type_id=2, name='phone', text_only=1)
    return session_type_website, session_type_phone

def create_admin_user():
    ''' Create a admin user that can access the admin dashboard.'''
    admin_user = User.objects.create_user(username='admin', email='@',
                                          password='admin')
    admin_user.is_superuser = True
    admin_user.save()
    Subject.objects.create(user_id=admin_user.id, date_created=TODAY)
    return admin_user
