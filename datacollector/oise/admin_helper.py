"""
    Helper functions for OISE admin view
"""

from datacollector.models import Bundle, Demographics_Oise, Session, Session_Task, \
                                 Subject, Subject_Bundle, Task, User
from django.contrib.auth.forms import UserCreationForm

import datetime

bundle = Bundle.objects.get(name_id='oise')


def get_oise_users():
    """
    Retrieve all OISE users.
    """
    subject_bundles = Subject_Bundle.objects.filter(bundle_id=bundle.bundle_id)

    subjects_object = []
    for subject_bundle in subject_bundles:
        subject_id = subject_bundle.subject_id
        subjects_object += [{
            'subject_id': subject_id,
            'demographics': get_demographic_information(subject_id)
        }]
    return subjects_object

def get_demographic_information(subject_id):
    """
    Retrieve demographic information for user with given subject_id
        :param subject_id:
    """
    demographics_object = Demographics_Oise.objects.filter(subject_id=subject_id).order_by('-id')
    if demographics_object:
        demographics_object = demographics_object[0]
        return {
            'gender': demographics_object.gender_id,
            'age': demographics_object.age,
            'grade': demographics_object.grade,
            'english_ability': demographics_object.english_ability
            }
    return {}

def get_session_information(subject_id):
    """
    Retrieve all sessions and session tasks for user with given subject_id
        :param subject_id:
    """
    sessions_object = []
    sessions = Session.objects.filter(subject_id=subject_id)
    for session in sessions:
        session_tasks_object = []
        session_tasks = Session_Task.objects.filter(session_id=session.session_id).order_by('order')
        for session_task in session_tasks:
            session_task_name = Task.objects.get(task_id=session_task.task_id).name
            session_tasks_object += [{
                'name': session_task_name,
                'date_completed': session_task.date_completed
            }]
        sessions_object += [{
            'session_id': session.session_id,
            'end_date': session.end_date,
            'session_tasks': session_tasks_object
        }]
    return sessions_object

def create_new_user(request):
    form = UserCreationForm(request.POST)
    print(form)
    if form.is_valid():

        today = datetime.datetime.now().date()

        # Save user
        cd = form.cleaned_data
        new_user = form.save()

        # Create a corresponding subject in the app
        new_subject = Subject.objects.create(user_id=new_user.id, date_created=today)

        # Create subject bundle
        Subject_Bundle.objects.create(subject=new_subject,
                                      bundle=bundle,
                                      active_startdate=today)
        print("User created")
        return True
    return False
