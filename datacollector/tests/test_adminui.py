"""Tests for functions of adminui.py"""

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client

from datacollector.models import Bundle, Subject, Subject_Bundle
from datacollector import adminui

TODAY = datetime.datetime.now().date()

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

class AdminUiUhnDashboardTestCase(TestCase):
    '''
        Class for uhn_dashboard() tests of adminui.py
    '''

    def setUp(self):
        '''
            setUp for AdminUiUhnDashboardTestCase
        '''

        # Create staff used with admin privileges
        admin_user = User.objects.create_user(username='admin', email='@',
                                              password='admin')
        admin_user.is_staff = True
        admin_user.save()
        Subject.objects.create(user_id=admin_user.id, date_created=TODAY)
        self.admin_user = admin_user

        # Create UHN web bundle
        uhn_bundle = Bundle.objects.create(bundle_id=1, name_id='uhn_web', bundle_token='123qwert')
        self.uhn_bundle = uhn_bundle

        # Create UHN web user
        uhn_user = User.objects.create_user(username='uhn', email='@',
                                            password='uhn')
        uhn_subject = Subject.objects.create(user_id=uhn_user.id, date_created=TODAY)
        Subject_Bundle.objects.create(subject_bundle_id=1, subject_id=uhn_subject.user_id,
                                      bundle_id=uhn_bundle.bundle_id, active_startdate=TODAY)
        self.uhn_web_user = uhn_subject

        # Client for performing HTTP requests
        self.client = Client()

    def test_get_uhn_dashboard_authenticated_user(self):
        '''
            test_get_uhn_dashboard_authenticated_user should return all bundles and associated
            users
        '''
        self.client.login(username=self.admin_user.username,
                          password=self.admin_user.password)
        response = self.client.get('/talk2me/uhn/admin')
        context = response.context

        self.assertTrue(context['is_authenticated'])
        self.assertEquals(context['bundle'].name_id, self.uhn_bundle.name_id)
        self.assertEquals(context['subject_bundle_users'][0].user_id, self.uhn_web_user.subject_id)
