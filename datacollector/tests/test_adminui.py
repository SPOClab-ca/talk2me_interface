"""Tests for functions of adminui.py"""

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.test.utils import setup_test_environment

from datacollector.models import Session, Subject
from datacollector import adminui

from utils import create_uhn_web_bundle, create_wch_web_bundle, create_uhn_web_subject, \
                  create_wch_web_subject, create_session_types, create_admin_user, \
                  create_uhn_phone_bundle, create_uhn_phone_subject, \
                  create_wch_phone_subject, create_wch_phone_bundle

TODAY = datetime.datetime.now().date()
setup_test_environment()


class AdminUiCreateSessionsTestCase(TestCase):
    '''
        Class for bundle_create_sessions() tests of adminui.py
    '''

    def setUp(self):
        '''
            setUp for AdminUiCreateSessionsTestCase
        '''

        # Create UHN web bundle and UHN web user
        self.uhn_web_bundle = create_uhn_web_bundle()
        self.uhn_web_subject = create_uhn_web_subject(self.uhn_web_bundle)

        # Create UHN phone bundle and UHN phone user
        self.uhn_phone_bundle = create_uhn_phone_bundle()
        self.uhn_phone_subject = create_uhn_phone_subject(self.uhn_phone_bundle)

        # Create WCH web bundle and WCH web user
        self.wch_web_bundle = create_wch_web_bundle()
        self.wch_web_subject = create_wch_web_subject(self.wch_web_bundle)

        # Create WCH phone bundle and WCH phone user
        self.wch_phone_bundle = create_wch_phone_bundle()
        self.wch_phone_subject = create_wch_phone_subject(self.wch_phone_bundle)

        create_session_types()

    def test_uhn_create_sessions(self):
        '''
            test_uhn_create_sessions should create sessions for user
        '''

        adminui.uhn_create_sessions(self.uhn_web_subject.user_id, self.uhn_web_bundle)
        sessions = Session.objects.filter(subject_id=self.uhn_web_subject.user_id)
        self.assertEquals(len(sessions), 7)

    def test_bundle_create_sessions(self):
        '''
            test_wch_create_sessions should create sessions for user
        '''
        bundle_subjects = [self.wch_web_subject, self.wch_phone_subject]
        bundles = [self.wch_web_bundle, self.wch_phone_bundle]
        for bundle_subject, bundle in zip(bundle_subjects, bundles):
            adminui.bundle_create_sessions(bundle_subject.user_id,
                                           bundle)
            sessions = Session.objects.filter(subject_id=self.wch_web_subject.user_id)
            self.assertEquals(len(sessions), 7)

class AdminUiUhnConsentSubmittedTestCase(TestCase):
    '''
        Class for uhn_consent_submitted() tests of adminui.py
    '''

    def setUp(self):
        '''
            setUp for AdminUiUhnConsentSubmittedTestCase
        '''

        # Create user with no consent submitted
        user = User.objects.create_user(username='testuser', email='@',
                                        password='testuser')
        subject = Subject.objects.create(user_id=user.id, date_created=TODAY)
        self.subject = subject

    def test_set_uhn_consent_submitted(self):
        '''
            test_set_uhn_consent_submitted should assign a value to date_consent_submitted
            and set the alternate_consent flag
        '''
        for is_alternate_decision_maker in [False, True]:
            adminui.uhn_consent_submitted(self.subject.user_id, is_alternate_decision_maker)
            self.assertIsNotNone(Subject.objects.get(user_id=self.subject.user_id).date_consent_submitted)
            self.assertEquals(Subject.objects.get(user_id=self.subject.user_id).consent_alternate, is_alternate_decision_maker)

    def test_update_consent(self):
        '''
            test_update_consent should assigna  value to date_consent_submitted
            and set alternate_consent flag.
        '''
        for is_alternate_decision_maker in [False, True]:
            adminui.update_consent(self.subject.user_id, is_alternate_decision_maker)
            self.assertIsNotNone(Subject.objects.get(user_id=self.subject.user_id).date_consent_submitted)
            self.assertEquals(Subject.objects.get(user_id=self.subject.user_id).consent_alternate, is_alternate_decision_maker)

class AdminUiUhnSessionTestCase(TestCase):
    '''
        Class for uhn_session() tests of adminui.py
    '''

    def setUp(self):
        '''
            setUp for AdminUiUhnSessionTestCase
        '''

        # Create staff user with admin privileges
        self.admin_user = create_admin_user()

        # Create UHN web bundle
        self.uhn_web_bundle = create_uhn_web_bundle()

        # Create UHN web user
        self.uhn_web_subject = create_uhn_web_subject(self.uhn_web_bundle)

        # Create sessions for UHN web user
        session_type_website, _ = create_session_types()
        Session.objects.create(subject=self.uhn_web_subject, start_date=TODAY, end_date=None, session_type=session_type_website)
        Session.objects.create(subject=self.uhn_web_subject, start_date=TODAY, end_date=None, session_type=session_type_website)

        self.client = Client()

    def test_get_uhn_dashboard_sessions(self):
        '''
            test_get_uhn_dashboard_sessions should return sessions for given user.
        '''

        self.client.login(username='admin', password='admin')
        response = self.client.get('/talk2me/uhn/admin/uhn_web/%d' % self.uhn_web_subject.user_id)
        context = response.context

        self.assertTrue(context['is_authenticated'])
        self.assertEquals(context['bundle'].name_id, self.uhn_web_bundle.name_id)
        self.assertEquals(len(context['sessions']), 2)

    def test_uhn_update_phone_pin(self):
        '''
            test_uhn_update_phone_pin should update the phone_pin of the subject
        '''

        uhn_phone_bundle = create_uhn_phone_bundle()
        uhn_phone_subject = create_uhn_phone_subject(uhn_phone_bundle)

        adminui.uhn_update_phone_pin(uhn_phone_subject.user_id, 1234)
        updated_subject = Subject.objects.get(user_id=uhn_phone_subject.user_id)
        self.assertEquals(updated_subject.phone_pin, '1234')

class AdminUiUhnDashboardTestCase(TestCase):
    '''
        Class for uhn_dashboard() tests of adminui.py
    '''

    def setUp(self):
        '''
            setUp for AdminUiUhnDashboardTestCase
        '''

        # Create staff user with admin privileges
        self.admin_user = create_admin_user()

        # Create UHN web bundle and UHN web user
        self.uhn_web_bundle = create_uhn_web_bundle()
        self.uhn_web_subject = create_uhn_web_subject(self.uhn_web_bundle)

        # Create WCH web bundle and WCH web user
        self.wch_web_bundle = create_wch_web_bundle()
        self.wch_web_subject = create_wch_web_subject(self.wch_web_bundle)

        self.client = Client()

    def test_get_uhn_dashboard_authenticated_user(self):
        '''
            test_get_uhn_dashboard_authenticated_user should return all bundles and associated
            users
        '''
        self.client.login(username='admin',
                          password='admin')
        response = self.client.get('/talk2me/uhn/admin/uhn_web')
        context = response.context

        self.assertTrue(context['is_authenticated'])
        self.assertEquals(context['bundle'].name_id, self.uhn_web_bundle.name_id)
        self.assertEquals(context['subject_bundle_users'][0].subject.user_id, self.uhn_web_subject.user_id)

    def test_wch_dashboard_admin(self):
        '''
            test_wch_dashboard lists all users in WCH study.
        '''
        self.client.login(username='admin',
                          password='admin')
        response = self.client.get('/talk2me/wch/admin/wch_web')
        context = response.context

        self.assertTrue(context['is_authenticated'])
        self.assertEquals(context['bundle'].name_id, self.wch_web_bundle.name_id)
        self.assertEquals(context['subject_bundle_users'][0].subject.user_id, self.wch_web_subject.user_id)

    def test_wch_dashboard_user(self):
        '''
            test_wch_dashboard should re-direct to home page for regular user.
        '''
        self.client.login(username='wch_web',
                          password='wch_web')
        response = self.client.get('/talk2me/wch/admin/wch_web')
        context = response.context

        self.assertIsNone(context)
