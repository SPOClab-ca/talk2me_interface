""" Test for functions of views.py"""

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client

from datacollector.models import (Bundle, Subject, Subject_Bundle, Language, Session,
                                  Session_Type, Session_Task, Task, Bundle_Task)
from datacollector import views

from utils import (create_web_user, create_uhn_web_bundle, create_uhn_phone_bundle,
                   create_uhn_user, create_session_types)

TODAY = datetime.datetime.now().date()

class ViewsIndexTestCase(TestCase):
    '''
        Class for index() tests of views.py
    '''

    def setUp(self):
        '''
            setUp for ViewsIndexTestCase
        '''

        # Authenticated user, no consent or demographics submitted
        User.objects.create_user(username='chloe', email='chloe@test',
                                 password='chloepw')

        # Authenticated user, consent and demographics submitted
        auth_user_con_dem = User.objects.create_user(username='user_con_dem', email='test@123',
                                                     password='user_con_dem')
        Subject.objects.create(user_id=auth_user_con_dem.id, date_created=TODAY,
                               date_consent_submitted=TODAY,
                               date_demographics_submitted=TODAY)

        self.client = Client()

        # Demographics options
        english_language = Language.objects.create(language_id=1, name='english', iso_code='EN',
                                                   is_official=1)
        self.language_options = [english_language]


    def test_get_index_unauthenticated(self):
        '''
            test_get_index_unauthenticated should set is_authenticated flag to false
        '''
        response = self.client.get('/talk2me/')
        context = response.context

        self.assertFalse(context['is_authenticated'])
        self.assertFalse(context['consent_submitted'])
        self.assertFalse(context['demographic_submitted'])
        self.assertFalse(context['usabilitysurvey_notsubmitted'])
        self.assertEquals(len(context['language_options']), 0)

    def test_get_index_authenticated(self):
        '''
            test_get_index_authenticated should populate demographics options
        '''
        self.client.login(username='chloe', password='chloepw')
        response = self.client.get('/talk2me/')
        context = response.context

        self.assertTrue(response.context['is_authenticated'])
        self.assertEquals(set(list(context['language_options'])), set(self.language_options))

    def test_get_index_consentdemographics(self):
        '''
            test_get_index_consent_demographics should not populate demographics options
        '''
        self.client.login(username='user_con_dem', password='user_con_dem')
        response = self.client.get('/talk2me/')
        context = response.context

        self.assertTrue(context['is_authenticated'])
        self.assertTrue(context['consent_submitted'])
        self.assertTrue(context['demographic_submitted'])
        self.assertEquals(len(context['language_options']), 0)

class ViewsGenerateSessionTestCase(TestCase):
    '''
        Class for generate_session() function of views.py
    '''

    def setUp(self):
        '''
            setUp for ViewsGenerateSessionTestCase
        '''

        # Create session types
        session_type_web = Session_Type.objects.create(session_type_id=1, name='web', text_only=0)
        session_type_phone = Session_Type.objects.create(session_type_id=2, name='phone', text_only=1)

        # Populate the DB with a few tasks
        bundle_task = Task.objects.create(task_id=1, name_id='task1', name='task1',
                                          instruction='instruction', default_order=1,
                                          is_order_fixed=0, default_delay=0,
                                          default_embedded_delay=0, is_active=1)
        active_task = Task.objects.create(task_id=2, name_id='task2', name='task2',
                                          instruction='inst', default_order=100,
                                          is_order_fixed=0, default_delay=0,
                                          default_embedded_delay=0, is_active=1)
        inactive_task = Task.objects.create(task_id=3, name_id='task3', name='task3',
                                            instruction='instructionnn', default_order=20,
                                            is_order_fixed=1, default_delay=0,
                                            default_embedded_delay=0, is_active=0)

        # Create a UHN user
        user_uhn = User.objects.create_user(username='user_uhn', email='@', password='user_uhn')
        subject_uhn_bundle = Subject.objects.create(user_id=user_uhn.id, date_created=TODAY,
                                                    date_consent_submitted=TODAY,
                                                    date_demographics_submitted=TODAY)
        Bundle.objects.create(bundle_id=1, name_id='uhn_web', bundle_token='123qwert')
        Subject_Bundle.objects.create(subject_bundle_id=1, subject_id=subject_uhn_bundle.user_id, bundle_id=1,
                                      active_startdate=TODAY)

        # Create a web user
        user_web = User.objects.create_user(username='user', email='@', password='web')
        subject_web = Subject.objects.create(user_id=user_web.id, date_created=TODAY,
                                             date_consent_submitted=TODAY,
                                             date_demographics_submitted=TODAY)

        # Assign task to bundle
        Bundle_Task.objects.create(bundle_task_id=1, bundle_id=1, task_id=bundle_task.task_id, default_num_instances=4)

        # Save on the object to re-use later
        self.subject_uhn_bundle = subject_uhn_bundle
        self.subject_web = subject_web
        self.session_type_web = session_type_web
        self.session_type_phone = session_type_phone
        self.bundle_task = bundle_task
        self.active_task = active_task
        self.inactive_task = inactive_task

    def test_generate_session_uhn(self):
        '''
            test_generate_session_uhn should only return tasks in UHN bundle
        '''

        uhn_session = views.generate_session(self.subject_uhn_bundle, self.session_type_web)
        session_tasks = Session_Task.objects.filter(session=uhn_session)

        self.assertEquals(session_tasks[0].task_id, self.bundle_task.task_id)

    def test_generate_session_web_user(self):
        '''
            test_generate_session_web_user should only return active tasks.
        '''

        web_session = views.generate_session(self.subject_web, self.session_type_web)
        session_tasks = Session_Task.objects.filter(session=web_session)
        self.assertEquals(len(session_tasks), 2)
        self.assertEquals(session_tasks[0].task_id, self.bundle_task.task_id)
        self.assertEquals(session_tasks[1].task_id, self.active_task.task_id)

class ViewsStartSessionTestCase(TestCase):
    '''
        Class for startsession() tests of views.py
    '''

    def setUp(self):
        '''
            setUp for ViewsStartSessionTestCase
        '''

        # Load session types
        create_session_types()

        # Create UHN web and phone bundles
        self.uhn_web_bundle = create_uhn_web_bundle()
        self.uhn_phone_bundle = create_uhn_phone_bundle()

        # Create generic web user
        self.web_user = create_web_user()

        # Create UHN web user
        self.uhn_web_user = create_uhn_user(self.uhn_web_bundle)

        # Create UHN phone user
        self.uhn_phone_user = create_uhn_user(self.uhn_phone_bundle)

        self.client = Client()

        # Validate that all users have no sessions
        for user in [self.web_user, self.uhn_web_user, self.uhn_phone_user]:
            user_sessions = Session.objects.filter(subject_id=user.id)
            self.assertEquals(len(user_sessions), 0)

    def test_startsession_web_user(self):
        '''
            test_startsession_web_user should sucessfully generate a new session.
        '''
        self.client.login(username=self.web_user.username,
                          password=self.web_user.username)
        self.client.get('/talk2me/startsession')

        sessions = Session.objects.filter(subject_id=self.web_user.id)
        self.assertEquals(len(sessions), 1)

    def test_start_session_uhn(self):
        '''
            test_startsession_uhn should not create a session for a UHN web user
            or a UHN phone user.
        '''
        for uhn_user in [self.uhn_web_user, self.uhn_phone_user]:
            self.client.login(username=uhn_user.username,
                              password=uhn_user.username)
            self.client.get('/talk2me/startsession')

            sessions = Session.objects.filter(subject_id=self.web_user.id)
            self.assertEquals(len(sessions), 0)
