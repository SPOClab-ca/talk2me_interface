# """Test for functions of phone.py"""

# import json
# import datetime

# from django.contrib.auth.models import User
#from django.test import TestCase
#from django.test import Client

# from datacollector.models import Session, Subject, Session_Phone_Duration
# from datacollector import phone
# from datacollector import lib

# from utils import create_session_types

# TODAY = datetime.datetime.now().date()

# class PhoneActiveSessionTestCase(TestCase):
#     '''
#         Class for active_session() API endpoint.
#     '''

#     def setUp(self):
#         '''
#             setUp for PhoneActiveSessionTestCase
#         '''

#         create_session_types()

#         self.client = Client()

#         # Create subject
#         user = User.objects.create_user(username='testuser', email='@',
#                                         password='testuser')
#         subject = Subject.objects.create(user_id=user.id, date_created=TODAY, phone_pin='1234')
#         self.subject = subject



#     def test_get_active_session(self):
#         '''
#             test_get_active_session should return the oldest active session.
#         '''

#         # Add some active sessions
#         old_session = Session.objects.create(session_id=1,
#                                              subject_id=self.subject.user_id,
#                                              start_date='2016-01-01',
#                                              session_type_id=2)
#         new_session = Session.objects.create(session_id=2,
#                                              subject_id=self.subject.user_id,
#                                              start_date='2016-12-12',
#                                              session_type_id=2)


#         self.client.login(username='testuser', password='testuser')
#         # print self.client
#         json_body = json.dumps({
#             'subject_id': self.subject.user_id,
#             'pin': self.subject.phone_pin,
#             'client_id': 1
#             })
#         json_body = {}
#         json_body['subject_id'] = self.subject.user_id
#         # print json_body
#         # auth_header = self.client.post('/talk2me/phone/login')
#         # print auth_header
#         phone.login({
#             'method': 'POST',
#             'body':
#                 {
#                 'subject_id': self.subject.user_id
#                 }
#             })
#         response = self.client.get('/talk2me/phone/active_session', HTTP_AUTHORIZATION='token')
#         print response

#     def test_get_active_session_none(self):
#         '''
#             test_get_active_session_none should return an error when there
#             are no active sessions.
#         '''

#         # Add pending sessions
#         Session.objects.create(session_id=1, subject_id=self.subject.user_id,
#                                start_date='2100-01-01', session_type_id=2)
#         Session.objects.create(session_id=2, subject_id=self.subject.user_id,
#                                start_date='2100-12-12', session_type_id=2)
#         self.client.login(username='testuser', password='testuser')
#         response = self.client.get('/talk2me/phone/active_session')