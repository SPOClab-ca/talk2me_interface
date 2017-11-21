"""Test for functions of phone.py"""

from django.test import TestCase
from datacollector.models import Session, Session_Phone_Duration
from datacollector import phone_helper

class CreateSessionPhoneDuration(TestCase):
    """ Tests for phone_helper.create_session_phone_duration """

    def add_to_database(self):
        """ Should add a new entry in database """
        session_id = '1234'
        duration = 120
        session = Session.objects.create(session_id=session_id)

        phone_helper.create_session_phone_duration(session=session, duration=duration)
        session_phone_duration = Session_Phone_Duration.objects.get(session=session)
        self.assertEquals(session_phone_duration.session_id, session_id)
        self.assertEquals(session_phone_duration.duration, duration)
