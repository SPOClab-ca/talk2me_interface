""" Test for functions of views.py"""

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client

from datacollector.models import (Bundle, Bundle_Task_Field_Value, Field_Data_Type, Field_Type, Subject,
                                  Subject_Bundle, Language, Session, Session_Type, Session_Task,
                                  Session_Task_Instance, Session_Task_Instance_Value, Task, Task_Field,
                                  Task_Field_Value, Value_Difficulty, Bundle_Task)
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

    # def test_get_index_authenticated(self):
    #     '''
    #         test_get_index_authenticated should populate demographics options
    #     '''
    #     self.client.login(username='chloe', password='chloepw')
    #     response = self.client.get('/talk2me/')
    #     context = response.context

    #     self.assertTrue(response.context['is_authenticated'])
    #     self.assertEquals(set(list(context['language_options'])), set(self.language_options))

    # def test_get_index_consentdemographics(self):
    #     '''
    #         test_get_index_consent_demographics should not populate demographics options
    #     '''
    #     self.client.login(username='user_con_dem', password='user_con_dem')
    #     response = self.client.get('/talk2me/')
    #     context = response.context

    #     self.assertTrue(context['is_authenticated'])
    #     self.assertTrue(context['consent_submitted'])
    #     self.assertTrue(context['demographic_submitted'])
    #     self.assertEquals(len(context['language_options']), 0)

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
        task_no_repeat = Task.objects.create(task_id=10, name_id='task1', name='task1',
                                             instruction='instruction', default_order=1,
                                             is_order_fixed=1, default_delay=0,
                                             default_embedded_delay=0, is_active=1)
        active_task = Task.objects.create(task_id=20, name_id='task2', name='task2',
                                          instruction='inst', default_order=100,
                                          is_order_fixed=0, default_delay=0,
                                          default_embedded_delay=0, is_active=1)
        inactive_task = Task.objects.create(task_id=30, name_id='task3', name='task3',
                                            instruction='instructionnn', default_order=20,
                                            is_order_fixed=1, default_delay=0,
                                            default_embedded_delay=0, is_active=0)
        task_repeat = Task.objects.create(task_id=40, name_id='bundle_task_allow_repeat',
                                          name='bundle_task_allow_repeat', instruction='',
                                          default_order=100, is_order_fixed=0, default_delay=0,
                                          default_embedded_delay=0, is_active=1)

        # Insert dummy field type, field data type, and value difficulty
        field_type = Field_Type.objects.create(field_type_id=1, name='display')
        field_data_type = Field_Data_Type.objects.create(field_data_type_id=1, name='text')
        value_difficulty = Value_Difficulty.objects.create(value_difficulty_id=1, name='low')
        Value_Difficulty.objects.create(value_difficulty_id=2, name='medium')
        Value_Difficulty.objects.create(value_difficulty_id=3, name='high')

        # Create task fields for tasks
        task_field_bundle_no_repeat = Task_Field.objects.create(task_field_id=1, name='',
                                                                task_id=task_no_repeat.task_id,
                                                                field_type_id=field_type.field_type_id,
                                                                field_data_type_id=field_data_type.field_data_type_id,
                                                                embedded_response=0, generate_value=1)
        task_field_bundle_repeat = Task_Field.objects.create(task_field_id=2, name='',
                                                             task_id=task_repeat.task_id,
                                                             field_type_id=field_type.field_type_id,
                                                             field_data_type_id=field_data_type.field_data_type_id,
                                                             embedded_response=0, generate_value=1)

        # Add task field values for the task fields
        task_field_value1 = Task_Field_Value.objects.create(task_field_value_id=1,
                                                            task_field_id=task_field_bundle_no_repeat.task_field_id,
                                                            value='task field value should not repeat',
                                                            difficulty_id=value_difficulty.value_difficulty_id)
        task_field_value2 = Task_Field_Value.objects.create(task_field_value_id=2,
                                                            task_field_id=task_field_bundle_no_repeat.task_field_id,
                                                            value='task field value should be different',
                                                            difficulty_id=value_difficulty.value_difficulty_id)
        task_field_value3 = Task_Field_Value.objects.create(task_field_value_id=3,
                                                            task_field_id=task_field_bundle_repeat.task_field_id,
                                                            value='this task field can have repeat instances',
                                                            difficulty_id=value_difficulty.value_difficulty_id)

        # Create a UHN user
        user_uhn = User.objects.create_user(username='user_uhn', email='@', password='user_uhn')
        subject_uhn_bundle = Subject.objects.create(user_id=user_uhn.id, date_created=TODAY,
                                                    date_consent_submitted=TODAY,
                                                    date_demographics_submitted=TODAY)
        uhn_web_bundle = Bundle.objects.create(bundle_id=3, name_id='uhn_web', bundle_token='123qwert')
        Subject_Bundle.objects.create(subject_bundle_id=1, subject_id=subject_uhn_bundle.user_id, bundle_id=uhn_web_bundle.bundle_id,
                                      active_startdate=TODAY)

        # Create a web user
        user_web = User.objects.create_user(username='user', email='@', password='web')
        subject_web = Subject.objects.create(user_id=user_web.id, date_created=TODAY,
                                             date_consent_submitted=TODAY,
                                             date_demographics_submitted=TODAY)

        # Assign task to bundle (this task cannot have repeat instances)
        bundle_task_no_repeat = Bundle_Task.objects.create(bundle_task_id=views.RIG_UHN_WEB_BUNDLE_TASK_ID,
                                                           bundle_id=uhn_web_bundle.bundle_id,
                                                           task_id=task_no_repeat.task_id,
                                                           default_num_instances=1)

        # Assign task to bundle (this task can have repeat instances)
        bundle_task_repeat = Bundle_Task.objects.create(bundle_task_id=1,
                                                        bundle_id=uhn_web_bundle.bundle_id,
                                                        task_id=task_repeat.task_id,
                                                        default_num_instances=1)


        # Assign task instances to bundle
        Bundle_Task_Field_Value.objects.create(bundle_task_field_value_id=1,
                                               bundle_task_id=bundle_task_no_repeat.bundle_task_id,
                                               task_field_value_id=task_field_value1.task_field_value_id)
        Bundle_Task_Field_Value.objects.create(bundle_task_field_value_id=2,
                                               bundle_task_id=bundle_task_no_repeat.bundle_task_id,
                                               task_field_value_id=task_field_value2.task_field_value_id)
        Bundle_Task_Field_Value.objects.create(bundle_task_field_value_id=3,
                                               bundle_task_id=bundle_task_repeat.bundle_task_id,
                                               task_field_value_id=task_field_value3.task_field_value_id)

        # Save on the object to re-use later
        self.subject_uhn_bundle = subject_uhn_bundle
        self.subject_web = subject_web
        self.session_type_web = session_type_web
        self.session_type_phone = session_type_phone
        self.bundle_task = bundle_task_no_repeat
        self.active_task = active_task
        self.inactive_task = inactive_task
        self.task_no_repeat = task_no_repeat
        self.task_repeat = task_repeat
        self.uhn_web_bundle = uhn_web_bundle
        self.field_type = field_type
        self.field_data_type = field_data_type

    def test_generate_session_uhn(self):
        '''
            test_generate_session_uhn should only return tasks in UHN bundle and respect
            their defined order
        '''

        uhn_session = views.generate_session(self.subject_uhn_bundle, self.session_type_web)
        session_tasks = Session_Task.objects.filter(session=uhn_session).order_by('order')
        self.assertEquals(session_tasks[0].task_id, self.bundle_task.task_id)
        self.assertEquals(session_tasks[1].task_id, self.task_repeat.task_id)

    # def test_generate_session_web_user(self):
    #     '''
    #         test_generate_session_web_user should only return active tasks.
    #     '''

    #     web_session = views.generate_session(self.subject_web, self.session_type_web)
    #     session_tasks = Session_Task.objects.filter(session=web_session)
    #     self.assertEquals(len(session_tasks), 3)

    def test_generate_session_uhn_multiple_sessions(self):
        '''
            test_generate_session_uhn_multiple_sessions should populate the session with
            different task instances if specified.
        '''

        first_session = views.generate_session(self.subject_uhn_bundle, self.session_type_web)
        first_session_task_no_repeat = Session_Task.objects.get(session_id=first_session.session_id, task_id=self.task_repeat.task_id)
        first_session_task_no_repeat_instance = Session_Task_Instance.objects.get(session_task_id=first_session_task_no_repeat.session_task_id)
        first_session_task_no_repeat_value = Session_Task_Instance_Value.objects.get(session_task_instance_id=first_session_task_no_repeat_instance.session_task_instance_id)
        first_session_task_repeat = Session_Task.objects.get(session_id=first_session.session_id, task_id=self.task_repeat.task_id)
        first_session_task_repeat_instance = Session_Task_Instance.objects.get(session_task_id=first_session_task_repeat.session_task_id)
        first_session_task_repeat_value = Session_Task_Instance_Value.objects.get(session_task_instance_id=first_session_task_repeat_instance.session_task_instance_id)

        second_session = views.generate_session(self.subject_uhn_bundle, self.session_type_web)
        second_session_task_no_repeat = Session_Task.objects.get(session_id=second_session.session_id, task_id=self.task_no_repeat.task_id)
        second_session_task_no_repeat_instance = Session_Task_Instance.objects.get(session_task_id=second_session_task_no_repeat.session_task_id)
        second_session_task_no_repeat_value = Session_Task_Instance_Value.objects.get(session_task_instance_id=second_session_task_no_repeat_instance.session_task_instance_id)
        second_session_task_repeat = Session_Task.objects.get(session_id=second_session.session_id, task_id=self.task_repeat.task_id)
        second_session_task_repeat_instance = Session_Task_Instance.objects.get(session_task_id=second_session_task_repeat.session_task_id)
        second_session_task_repeat_value = Session_Task_Instance_Value.objects.get(session_task_instance_id=second_session_task_repeat_instance.session_task_instance_id)

        self.assertEqual(first_session_task_repeat_value.value, second_session_task_repeat_value.value)
        self.assertNotEqual(first_session_task_no_repeat_value.value, second_session_task_no_repeat_value.value)

    def test_delete_session(self):
        '''
            test_delete_session should remove all session tasks
        '''

        session = views.generate_session(self.subject_uhn_bundle, self.session_type_web)

        self.assertEqual(len(Session_Task.objects.filter(session_id=session.session_id)), 2)

        views.delete_session(session.session_id)
        self.assertEqual(len(Session_Task.objects.filter(session_id=session.session_id)), 0)
        self.assertEqual(len(Session.objects.filter(session_id=session.session_id)), 0)

    def test_generate_session_vocabulary_task(self):
        '''
            test_generate_session_vocabulary_task should generate task instances with
            3 words of low difficulty, 2 words of medium difficulty, and 1 word of high difficulty
        '''

        num_instances_vocabulary = 6
        num_instances_vocabulary_low = 3
        num_instances_vocabulary_medium = 2
        num_instances_vocabulary_high = 1

        # Get difficulties
        low_difficulty = Value_Difficulty.objects.get(value_difficulty_id=1)
        medium_difficulty = Value_Difficulty.objects.get(value_difficulty_id=2)
        high_difficulty = Value_Difficulty.objects.get(value_difficulty_id=3)

        # Create vocabulary task
        vocabulary_task = Task.objects.create(task_id=views.VOCABULARY_TASK_ID, name_id='vocabulary', name='vocabulary',
                                              instruction='instruction', default_order=1,
                                              is_order_fixed=1, default_delay=0,
                                              default_embedded_delay=0, is_active=1)
        bundle_task_vocabulary = Bundle_Task.objects.create(bundle_task_id=views.VOCABULARY_UHN_WEB_BUNDLE_TASK_ID,
                                                            bundle_id=self.uhn_web_bundle.bundle_id,
                                                            task_id=vocabulary_task.task_id,
                                                            default_num_instances=num_instances_vocabulary)

        # Create task field for vocabulary task
        task_field_vocabulary = Task_Field.objects.create(task_field_id=10, name='',
                                                          task_id=vocabulary_task.task_id,
                                                          field_type_id=self.field_type.field_type_id,
                                                          field_data_type_id=self.field_data_type.field_data_type_id,
                                                          embedded_response=0, generate_value=1)

        # Insert some values for vocabulary task instance
        for difficulty in [low_difficulty, medium_difficulty, high_difficulty]:
            for i in range(3):
                Task_Field_Value.objects.create(task_field_value_id=difficulty.value_difficulty_id * 100 + i,
                                                task_field_id=task_field_vocabulary.task_field_id,
                                                value='word',
                                                difficulty_id=difficulty.value_difficulty_id)
                Bundle_Task_Field_Value.objects.create(bundle_task_field_value_id=difficulty.value_difficulty_id * 100 + i,
                                                       bundle_task_id=bundle_task_vocabulary.bundle_task_id,
                                                       task_field_value_id=difficulty.value_difficulty_id * 100 + i)

        # Create session
        vocabulary_session = views.generate_session(self.subject_uhn_bundle, self.session_type_web)
        vocabulary_session_tasks = Session_Task.objects.get(session_id=vocabulary_session.session_id, task_id=vocabulary_task.task_id)
        vocabulary_session_task_instance_ids = Session_Task_Instance.objects.filter(session_task_id=vocabulary_session_tasks.session_task_id)
        vocabulary_session_task_instances_low = Session_Task_Instance_Value.objects.filter(session_task_instance_id__in=vocabulary_session_task_instance_ids,
                                                                                           difficulty_id=low_difficulty.value_difficulty_id)
        vocabulary_session_task_instances_medium = Session_Task_Instance_Value.objects.filter(session_task_instance_id__in=vocabulary_session_task_instance_ids,
                                                                                              difficulty_id=medium_difficulty.value_difficulty_id)
        vocabulary_session_task_instances_high = Session_Task_Instance_Value.objects.filter(session_task_instance_id__in=vocabulary_session_task_instance_ids,
                                                                                            difficulty_id=high_difficulty.value_difficulty_id)

        self.assertEquals(len(vocabulary_session_task_instances_low), num_instances_vocabulary_low)
        self.assertEquals(len(vocabulary_session_task_instances_medium), num_instances_vocabulary_medium)
        self.assertEquals(len(vocabulary_session_task_instances_high), num_instances_vocabulary_high)

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

    # def test_startsession_web_user(self):
    #     '''
    #         test_startsession_web_user should sucessfully generate a new session.
    #     '''
    #     self.client.login(username=self.web_user.username,
    #                       password=self.web_user.username)
    #     self.client.get('/talk2me/startsession')

    #     sessions = Session.objects.filter(subject_id=self.web_user.id)
    #     self.assertEquals(len(sessions), 1)

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
