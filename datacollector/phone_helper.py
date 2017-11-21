""" Helper functions for phone.py API calls """

from datacollector.models import Session_Phone_Duration

def create_session_phone_duration(session, duration):
    Session_Phone_Duration.objects.create(session=session, duration=duration)