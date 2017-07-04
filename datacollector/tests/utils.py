""" Helper functions used for testing. """

import datetime

from django.contrib.auth.models import User
from datacollector.models import Bundle, Session_Type, Subject, Subject_Bundle

TODAY = datetime.datetime.now().date()

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

def create_uhn_web_bundle():
    ''' Create a UHN web bundle and return it.'''
    uhn_bundle = Bundle.objects.create(bundle_id=3, name_id='uhn_web', bundle_token='123qwert')
    return uhn_bundle

def create_uhn_phone_bundle():
    ''' Create a UHN phone bundle and return it.'''
    phone_bundle = Bundle.objects.create(bundle_id=4, name_id='uhn_phone', bundle_token='456qwert')
    return phone_bundle

def create_uhn_web_subject(uhn_bundle):
    ''' Create a UHN web user and subject and return the UHN web user.'''
    uhn_user = User.objects.create_user(username='uhn', email='@',
                                        password='uhn')
    uhn_subject = Subject.objects.create(user_id=uhn_user.id, date_created=TODAY)
    Subject_Bundle.objects.create(subject_bundle_id=1, subject_id=uhn_subject.user_id,
                                  bundle_id=uhn_bundle.bundle_id, active_startdate=TODAY)
    return uhn_subject

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
