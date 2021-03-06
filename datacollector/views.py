""" Functions for views """

from django import forms
from django.db.models import Q, Count, Sum
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
import simplejson
from django.views.decorators.csrf import csrf_exempt
from datacollector.forms import *
from datacollector.models import *
from csc2518.settings import STATIC_URL
from csc2518.settings import SUBSITE_ID
from csc2518.settings import UHN_STUDY, OISE_STUDY, WCH_STUDY

import copy
import datetime
import json
import random
import re

import crypto
import emails
import notify

# Set up mail authentication
global email_username, email_name, website_hostname
email_username = Settings.objects.get(setting_name="system_email").setting_value
email_name = Settings.objects.get(setting_name="system_email_name").setting_value
website_hostname = Settings.objects.get(setting_name="website_hostname").setting_value
website_name = Settings.objects.get(setting_name="website_name").setting_value

# Globals
global global_passed_vars, date_format, age_limit, regex_email, regex_date, colour_lookup
global_passed_vars = { "website_id": "talk2me", "website_name": website_name, "website_email": email_username, "uhn_study": 'uhn', "oise_study": 'oise', "wch_study": 'wch' }
website_root = '/'
if SUBSITE_ID: website_root += SUBSITE_ID
uhn_website_root = website_root + UHN_STUDY
OISE_WEBSITE_ROOT = website_root + OISE_STUDY
WCH_WEBSITE_ROOT = website_root + WCH_STUDY

colour_lookup = {'red': 'e41a1c', 'green': '4daf4a', 'blue': '377eb8', 'brown': '6f370f', 'purple': '984ea3'}

date_format = "%Y-%m-%d"
age_limit = 18
regex_email = re.compile(r"[^@]+@[^@]+\.[^@]+")
regex_date = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")

# bundle-specific variable
UHN_WEB_BUNDLE_ID = 3
UHN_PHONE_BUNDLE_ID = 4
OISE_BUNDLE_ID = 5

# Task ID variables
VOCABULARY_TASK_ID = 1
RIG_TASK_ID = 12
GENERAL_DISPOSITION_TASK_ID = 13

# Bundle task ID variables
VOCABULARY_UHN_WEB_BUNDLE_TASK_ID = 5
VOCABULARY_UHN_PHONE_BUNDLE_TASK_ID = 12
PICTURE_DESCRIPTION_UHN_WEB_BUNDLE_TASK_ID = 6
RIG_UHN_WEB_BUNDLE_TASK_ID = 9
RIG_UHN_PHONE_BUNDLE_TASK_ID = 15

OISE_BUNDLE = Bundle.objects.get(name_id='oise')
FLUENCY_READING_OISE_TASK = Task.objects.get(name_id='reading_fluency')
FLUENCY_READING_OISE_BUNDLE_TASK_ID = Bundle_Task.objects\
                                                 .get(bundle=OISE_BUNDLE, \
                                                      task=FLUENCY_READING_OISE_TASK)\
                                                 .bundle_task_id
WORD_SOUNDS_OISE_TASK = Task.objects.get(name_id='word_sounds_oise')
WORD_SOUNDS_OISE_BUNDLE_TASK_ID = Bundle_Task.objects\
                                             .get(bundle=OISE_BUNDLE, \
                                                  task=WORD_SOUNDS_OISE_TASK)\
                                             .bundle_task_id
OISE_BUNDLE_TASK_IDS = [FLUENCY_READING_OISE_BUNDLE_TASK_ID, WORD_SOUNDS_OISE_BUNDLE_TASK_ID]

# Difficulty ID variables
DIFFICULTY_LOW_ID = 1
DIFFICULTY_MEDIUM_ID = 2
DIFFICULTY_HIGH_ID = 3

NUM_TASK_INSTANCES_UHN = 5

# Common lib functions ------------------------------------------------------

def delete_session(session_id):
    '''
        Function for deleting a session. Takes as input a session ID and deletes
        the session, as well as its associated tasks, task instances, and session
        response objects. Returns True upon completion.
    '''

    # Get session tasks associated with session id
    session_tasks = Session_Task.objects.filter(session_id=session_id)

    # Get session task instances associated with each session task id
    for session_task in session_tasks:
        session_task_instances = Session_Task_Instance.objects.filter(session_task_id=session_task.session_task_id)
        # Get response object associated with each session task instance id, and delete it
        for session_task_instance in session_task_instances:
            Session_Response.objects.get(session_task_instance_id=session_task_instance.session_task_instance_id).delete()

            # Once the session response is deleted, delete the session task instance
            session_task_instance.delete()

        # Once all the session task instances are deleted, delete the session task
        session_task.delete()

    # Now that all the session tasks are deleted, remove the session
    Session.objects.get(session_id=session_id).delete()

    return True

def get_ordered_task_fields_and_values(bundle_task_id):
    task_field_values = Bundle_Task_Field_Value.objects\
                                               .filter(bundle_task_id=bundle_task_id)\
                                               .order_by('bundle_task_field_value_id')
    task_field_value_ids = [x.task_field_value_id for x in task_field_values]

    # OISE Reading Fluency task needs to be:
    # short story 1, short story 2, MC question, MC question,
    #   short story 3, MC question, MC question, short story 4, \
    #   MC question, MC question
    if bundle_task_id == FLUENCY_READING_OISE_BUNDLE_TASK_ID:
        short_story_task_field=Task_Field.objects \
                                    .get(name='reading_fluency_story')
        short_stories = Task_Field_Value.objects \
                            .filter(task_field_value_id__in=task_field_value_ids,\
                                    task_field_id=short_story_task_field.task_field_id)
        mcq_task_field = Task_Field.objects.get(name='reading_fluency_question')
        mc_questions = Task_Field_Value.objects \
                        .filter(task_field_value_id__in=task_field_value_ids, \
                                task_field_id=mcq_task_field.task_field_id)
        ordered_task_fields = [short_story_task_field, \
                                short_story_task_field, mcq_task_field, mcq_task_field, \
                                short_story_task_field, mcq_task_field, mcq_task_field, \
                                short_story_task_field, mcq_task_field, mcq_task_field,]
        ordered_task_field_values = [short_stories[0], \
                                        short_stories[1], mc_questions[1], \
                                        mc_questions[2], short_stories[2], \
                                        mc_questions[3], mc_questions[4], \
                                        short_stories[3], mc_questions[5], \
                                        mc_questions[6]]
    elif bundle_task_id == WORD_SOUNDS_OISE_BUNDLE_TASK_ID:
        audio_example_task_field = Task_Field.objects.get(name='word_sounds_example')
        audio_examples = Task_Field_Value.objects\
                                         .filter(task_field_value_id__in=task_field_value_ids, \
                                                 task_field_id=audio_example_task_field)
        feedback_task_field = Task_Field.objects.get(name='word_sounds_feedback')
        feedback = Task_Field_Value.objects\
                                   .filter(task_field_value_id__in=task_field_value_ids, \
                                           task_field_id=feedback_task_field)

        audio_task_field = Task_Field.objects.get(name='word_sounds_audio')
        audio_tasks = Task_Field_Value.objects\
                                      .filter(task_field_value_id__in=task_field_value_ids, \
                                              task_field_id=audio_task_field)

        text_instruction_task_field = Task_Field.objects.get(name='word_sounds_text_instruction')
        text_instructions = Task_Field_Value.objects\
                                            .filter(task_field_value_id__in=task_field_value_ids, \
                                                    task_field_id=text_instruction_task_field)

        text_example_task_field = Task_Field.objects.get(name='word_sounds_text_example')
        text_examples = Task_Field_Value.objects\
                                        .filter(task_field_value_id__in=task_field_value_ids, \
                                                task_field_id=text_example_task_field)

        text_task_field = Task_Field.objects.get(name='word_sounds_text')
        text_tasks = Task_Field_Value.objects\
                                     .filter(task_field_value_id__in=task_field_value_ids, \
                                             task_field_id=text_task_field)

        ordered_task_fields = [audio_example_task_field] + \
                              [audio_task_field]*2 + [feedback_task_field] + \
                              [audio_task_field]*10 + \
                              [text_instruction_task_field, text_example_task_field] + \
                              [text_task_field]*2 + [feedback_task_field] + \
                              [text_task_field]*10 + [text_instruction_task_field]
        ordered_task_field_values = [audio_examples[0], audio_tasks[0], audio_tasks[1], feedback[0]] + \
                                    list(audio_tasks[2:]) + \
                                    [text_instructions[0], text_examples[0]] + \
                                    [text_tasks[0], text_tasks[1], feedback[1]] + \
                                    list(text_tasks[2:]) + [text_instructions[1]]

    return ordered_task_fields, ordered_task_field_values

def generate_session(subject, session_type):
    '''
        Function for generating a new session.
    '''

    # If the user has any active task bundles, then generate the tasks from the bundles only.
    # The active date range for the bundle is inclusive.
    today = datetime.datetime.now().date()
    active_bundles = Subject_Bundle.objects.filter( Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today )
    active_tasks = []
    active_tasks_num_instances = {} # key=task_id, value=num_instances in bundle
    active_bundle_tasks = {} # key=task_id, value=bundle_task
    if active_bundles:

        for subj_bundle in active_bundles:
            bundle_id = subj_bundle.bundle.name_id
            bundle_tasks = subj_bundle.bundle.bundle_task_set.all()

            if bundle_id == 'uhn_web':
                while len(bundle_tasks) > NUM_TASK_INSTANCES_UHN:
                    idx_to_remove = random.randint(0, len(bundle_tasks) - 1)
                    id_task_to_remove = bundle_tasks[idx_to_remove].task.task_id
                    if id_task_to_remove != GENERAL_DISPOSITION_TASK_ID:
                        bundle_tasks = bundle_tasks[:idx_to_remove] + bundle_tasks[idx_to_remove+1:]

            # If necessary, add another task instance. (Note: This might not be necessary, given current
            # number of tasks in the bundle).
            elif bundle_id == 'uhn_phone':
                while len(bundle_tasks) < NUM_TASK_INSTANCES_UHN:
                    idx_to_add = random.randint(0, len(bundle_tasks) - 1)
                    id_task_to_add = bundle_tasks[idx_to_add].task.task_id
                    if id_task_to_add != GENERAL_DISPOSITION_TASK_ID:
                        bundle_tasks = bundle_tasks[:] + [bundle_tasks[idx_to_add]]

            # For each Bundle_Task record the task and the num instances
            for x in bundle_tasks:
                active_tasks += [x.task]
                active_tasks_num_instances[x.task.task_id] = x.default_num_instances
                active_bundle_tasks[x.task.task_id] = x



    # Otherwise, generate all active tasks.
    else:
        active_tasks = Task.objects.filter(is_active=1)
        if session_type.text_only:
            active_tasks = Task.objects.filter(is_active=1, instruction_phone__isnull=False)

    active_task_ids = [t.task_id for t in active_tasks]

    # Randomly shuffle the order of the tasks in the session, except for the tasks with fixed order (e.g., disposition task)
    active_task_order = [(t.default_order, t.is_order_fixed) for t in active_tasks]
    idx_to_shuffle = [i for i, x in enumerate(active_task_order) if x[1] == 0]
    tasks_to_shuffle = [active_task_order[i] for i in idx_to_shuffle]
    random.shuffle(tasks_to_shuffle)
    for i in range(len(idx_to_shuffle)):
        active_task_order[idx_to_shuffle[i]] = tasks_to_shuffle[i]

    startdate = datetime.datetime.now()
    new_session = Session.objects.create(subject=subject, start_date=startdate, end_date=None, session_type=session_type)

    # Select random task questions for the session, OR use the specified task questions if they
    # are provided for the bundle.
    counter_task = 0
    for task_id in active_task_ids:
        task = Task.objects.get(task_id=task_id)

        bundle_task = None
        if task_id in active_bundle_tasks:
            bundle_task = active_bundle_tasks[task_id]

        # Check if there is a specified number of instances in the bundle task.
        if task_id in active_tasks_num_instances:
            num_instances = active_tasks_num_instances[task_id]
        # Otherwise, use default task num instances.
        else:
            num_instances = task.default_num_instances

        if not num_instances:
            # Sum up the instances for each display field for the task
            num_instances = Task_Field.objects.filter(task=task, field_type__name='display').aggregate(Sum('default_num_instances'))['default_num_instances__sum']
        task_order = task.default_order
        shuffled_order = active_task_order[counter_task][0]
        task_delay = task.default_delay
        task_embedded_delay = task.default_embedded_delay

        # Add the task to the current session in the database
        new_task = Session_Task.objects.create(session=new_session, task=task, order=shuffled_order, delay=task_delay, embedded_delay=task_embedded_delay)

        # Update the database to reflect <num_instances> instances of this task for this session
        new_task_instances = []
        for num in range(num_instances):
            new_task_instance = Session_Task_Instance.objects.create(session_task=new_task)
            # Add a response entry for each task instance
            new_task_instance_response = Session_Response.objects.create(session_task_instance=new_task_instance)

            new_task_instances += [new_task_instance]

        # Select random field values for each of the new task instances
        # (only for the fields that need to have generated values, i.e. for display fields)
        task_fields_display = Task_Field.objects.filter(task=task, field_type__name='display', generate_value=1)

        # For each display field, select random <num_instances> which the user hasn't seen before OR use the
        # specified task instances values for the bundle task.
        cumulative_field_instances = 0

        # For OISE-specific tasks that follow a weird ordering
        if bundle_task and bundle_task.bundle_task_id in OISE_BUNDLE_TASK_IDS:

            ordered_task_fields, ordered_task_field_values = get_ordered_task_fields_and_values(bundle_task.bundle_task_id)
            for index_instance in range(len(ordered_task_fields)):
                instance_value = ordered_task_field_values[index_instance]
                field = ordered_task_fields[index_instance]
                new_session_value = Session_Task_Instance_Value.objects.create(session_task_instance=new_task_instances[cumulative_field_instances+index_instance], task_field=field, value=instance_value.value, value_display=instance_value.value_display, difficulty=instance_value.difficulty)

                # Using the task field value ("instance_value"), update the expected session response
                Session_Response.objects.filter(session_task_instance=new_task_instances[cumulative_field_instances+index_instance]).update(value_expected=instance_value.response_expected)

                # If there are any associated fields (e.g., answer field instances associated with the currently selected question field instances), add them to the session as well.
                # Note that for select options, all options must be added, not just the one that is the correct response.
                linked_field_instances = list(Task_Field_Value.objects.filter(Q(assoc=instance_value) | Q(assoc=instance_value.assoc)).exclude(task_field=field).exclude(assoc__isnull=True))


                for linked_instance in linked_field_instances:
                    score = 0
                    if linked_instance.assoc.task_field_value_id == instance_value.task_field_value_id:
                        score = 1

                    new_session_value = Session_Task_Instance_Value.objects.create(session_task_instance=new_task_instances[cumulative_field_instances+index_instance], task_field=linked_instance.task_field, value=linked_instance.value, value_display=linked_instance.value_display, difficulty=linked_instance.difficulty)

            cumulative_field_instances += len(ordered_task_fields)
        for field in task_fields_display:

            # If the field doesn't have a specified number of instances, then use the task-level number of instances.
            field_num_instances = field.default_num_instances
            if not field_num_instances:
                field_num_instances = num_instances

            existing_instances = Session_Task_Instance_Value.objects.filter(task_field=field, session_task_instance__session_task__session__subject=subject)
            existing_values = [v.value for v in existing_instances]

            selected_values = []

            # If there are specified task field values in the bundle task, select those.
            specified_values = []
            specified_values_from_db = []
            if bundle_task is not None:
                specified_values_from_db = Bundle_Task_Field_Value.objects.filter(bundle_task_id=bundle_task.bundle_task_id).order_by('bundle_task_field_value_id')

            if len(specified_values_from_db) > 0:
                bundle_id = bundle_task.bundle.bundle_id
                if bundle_id == UHN_WEB_BUNDLE_ID or bundle_id == UHN_PHONE_BUNDLE_ID:
                    # Select from Bundle_Task_Field_Value instances in a random order
                    specified_values = [specified_value for specified_value in specified_values_from_db]
                    random.shuffle(specified_values)

                    # If vocabulary (5, 12), picture_description (6), and RIG (9, 15) make sure it's a value that hasn't been already selected or seen by the subject in previous sessions
                    bundle_task_ids_no_repeat = [VOCABULARY_UHN_WEB_BUNDLE_TASK_ID, VOCABULARY_UHN_PHONE_BUNDLE_TASK_ID, PICTURE_DESCRIPTION_UHN_WEB_BUNDLE_TASK_ID,
                                                 RIG_UHN_WEB_BUNDLE_TASK_ID, RIG_UHN_PHONE_BUNDLE_TASK_ID]
                    bundle_task_id = bundle_task.bundle_task_id
                    if bundle_task_id in bundle_task_ids_no_repeat:

                        # For vocabulary task, we want a specific number of easy/medium/hard task instances
                        if bundle_task_id == VOCABULARY_UHN_PHONE_BUNDLE_TASK_ID or bundle_task_id == VOCABULARY_UHN_WEB_BUNDLE_TASK_ID:
                            # Retrieve from DB
                            vocabulary_values_low_from_db = Bundle_Task_Field_Value.objects.filter(bundle_task_id=bundle_task_id,
                                                                                                   task_field_value__difficulty_id=DIFFICULTY_LOW_ID)
                            vocabulary_values_medium_from_db = Bundle_Task_Field_Value.objects.filter(bundle_task_id=bundle_task_id,
                                                                                                      task_field_value__difficulty_id=DIFFICULTY_MEDIUM_ID)
                            vocabulary_values_high_from_db = Bundle_Task_Field_Value.objects.filter(bundle_task_id=bundle_task_id,
                                                                                                    task_field_value__difficulty_id=DIFFICULTY_HIGH_ID)

                            # Remove instances that were already seen
                            filtered_vocabulary_values_low = [vocabulary_value for vocabulary_value in vocabulary_values_low_from_db if vocabulary_value.task_field_value.value not in existing_values]
                            filtered_vocabulary_values_medium = [vocabulary_value for vocabulary_value in vocabulary_values_medium_from_db if vocabulary_value.task_field_value.value not in existing_values]
                            filtered_vocabulary_values_high = [vocabulary_value for vocabulary_value in vocabulary_values_high_from_db if vocabulary_value.task_field_value.value not in existing_values]

                            # Shuffle
                            random.shuffle(filtered_vocabulary_values_low)
                            random.shuffle(filtered_vocabulary_values_medium)
                            random.shuffle(filtered_vocabulary_values_high)

                            # Draw 3 easy words, 2 medium words, and 1 hard word
                            selected_values = [value.task_field_value for value in filtered_vocabulary_values_low[:3] + filtered_vocabulary_values_medium[:2] + filtered_vocabulary_values_high[:1]]

                        else:
                            specified_values = [specified_value for specified_value in specified_values if specified_value.task_field_value.value not in existing_values]
                            selected_values = [x.task_field_value for x in specified_values[:field_num_instances]]
                    else:
                        selected_values = [x.task_field_value for x in specified_values[:field_num_instances]]
                elif bundle_id == OISE_BUNDLE_ID and bundle_task.bundle_task_id in OISE_BUNDLE_TASK_IDS:
                    continue

                else:
                    specified_values = specified_values_from_db
                    selected_values = [x.task_field_value for x in specified_values[len(existing_instances):len(existing_instances)+field_num_instances]]

            # Otherwise, randomly select values that haven't been viewed yet.
            else:
                # Add to selected values. Make sure not to add field values that are associated with each other, or are already selected, or have been seen by the subject before in previous sessions. NB: here we are assuming that the total number of values for each field in the db is at least as big as the default number of instances for the field.
                limits = []
                bundle_id = None
                if bundle_task:
                    bundle_id = bundle_task.bundle.bundle_id
                    if bundle_id == OISE_BUNDLE_ID:
                        selected_values = Task_Field_Value.objects.filter(task_field=field)
                while len(selected_values) < field_num_instances:

                    field_values = Task_Field_Value.objects.filter(task_field=field,*limits).exclude(value__in=existing_values)
                    if field_values:
                        selected_values += [random.choice(field_values)]
                    else:
                        # If there aren't any results, relax the query by restricting only to values that haven't been seen before
                        field_values = Task_Field_Value.objects.filter(task_field=field).exclude(value__in=existing_values)
                        if field_values:
                            selected_values += [random.choice(field_values)]
                        else:
                            # If there aren't any results (i.e., the subject has seen all possible values for this field), then relax the query by just selecting values that are different from the currently selected values (i.e., don't want any repeating values in the current session if possible, which should be the case as long as the number of values for the field is greater than the default number of instances for the field).
                            field_values = Task_Field_Value.objects.filter(task_field=field,*limits)
                            if field_values:
                                selected_values += [random.choice(field_values)]
                            else:
                                # If there still aren't any results (i.e., the subject has seen all possible values for this field), relax the query completely by selecting any random field value, regardless of whether the subject has seen it before or whether it has been selected for the current session (i.e., allow repeats).
                                field_values = Task_Field_Value.objects.filter(task_field=field)
                                if field_values:
                                    selected_values += [random.choice(field_values)]
                                else:
                                    # The database doesn't contain any entries for this task field.
                                    # Fail, display an error page.
                                    return HttpResponseRedirect(website_root + 'error/501')

                    # Build limit query with Q objects: enforce no repetition of the same item in the same task instance,
                    # and no selection of mutually associated items in the same task instance.
                    selected_assoc_ids = [item.assoc_id for item in selected_values]
                    selected_ids = [item.task_field_value_id for item in selected_values]
                    limit_assoc = [~Q(task_field_value_id=i) for i in selected_assoc_ids if i]
                    limit_id = [~Q(task_field_value_id=i) for i in selected_ids if i]
                    limits = limit_assoc + limit_id

                    # Special case: Stroop task. Enforce the special restriction that consecutive items are not of
                    # the same ink colour, and do not spell out the same colour word.
                    if task.name_id == "stroop" and selected_values:
                        limits += [ ~Q(response_expected = selected_values[-1].response_expected), \
                                    ~Q(value_display = selected_values[-1].value_display) ]

            for index_instance in range(field_num_instances):
                instance_value = selected_values[index_instance]
                new_session_value = Session_Task_Instance_Value.objects.create(session_task_instance=new_task_instances[cumulative_field_instances+index_instance], task_field=field, value=instance_value.value, value_display=instance_value.value_display, difficulty=instance_value.difficulty)

                # Using the task field value ("instance_value"), update the expected session response
                Session_Response.objects.filter(session_task_instance=new_task_instances[cumulative_field_instances+index_instance]).update(value_expected=instance_value.response_expected)

                # If there are any associated fields (e.g., answer field instances associated with the currently selected question field instances), add them to the session as well.
                # Note that for select options, all options must be added, not just the one that is the correct response.
                linked_field_instances = list(Task_Field_Value.objects.filter(Q(assoc=instance_value) | Q(assoc=instance_value.assoc)).exclude(task_field=field).exclude(assoc__isnull=True))

                # Unless the order of the options is supposed to remain fixed (e.g.,yes/no questions), we need to scramble
                # the order of the linked instances randomly, so the subject won't know the order of the correct options.
                if not field.preserve_order:
                    random.shuffle(linked_field_instances)

                for linked_instance in linked_field_instances:
                    score = 0
                    if linked_instance.assoc.task_field_value_id == instance_value.task_field_value_id:
                        score = 1

                    new_session_value = Session_Task_Instance_Value.objects.create(session_task_instance=new_task_instances[cumulative_field_instances+index_instance], task_field=linked_instance.task_field, value=linked_instance.value, value_display=linked_instance.value_display, difficulty=linked_instance.difficulty)

            cumulative_field_instances += field_num_instances
        counter_task += 1

    return new_session

# END of common lib functions ------------------------------------------------------


def index(request):

    # Authenticate current user. If no user logged in, redirect to login page.
    is_authenticated = False
    completed_sessions = []
    pending_sessions = []
    active_sessions = []
    active_notifications = []
    consent_submitted = False
    demographic_submitted = False
    gender_options = []
    language_options = []
    language_other = []
    language_fluency_options = []
    ethnicity_options = []
    education_options = []
    dementia_options = []
    country_res_options = []
    form_languages_fluency = []
    form_languages_other_fluency = []
    form_errors = []
    usabilitysurvey_notsubmitted = False
    subject_bundle = None
    bundle_id = None
    bundle_token = None
    user_id = None
    phone_pin = None
    start_new_phone_session = True

    if 'bid' in request.GET and 'bt' in request.GET:
        bundle_id = request.GET['bid']
        bundle_token = request.GET['bt']

    if request.user.is_authenticated():
        is_authenticated = True

        user_id = request.user.id
        phone_pin = Subject.objects.get(user_id=user_id).phone_pin

        if request.method == 'POST':
            date_submitted = datetime.datetime.now()
            form_type = request.POST['form_type']
            if form_type == 'consent':

                # Perform form validation first
                # - check that consent has been provided
                if 'radio_consent' not in request.POST:
                    form_errors += ['You did not provide consent by selecting the appropriate option. If you do not consent to this form, you cannot use ' + str(global_passed_vars['website_name']) + "." ]

                # - check that if any of the email-related options has been selected, the email address is provided
                user_email = ""
                if 'email_address' in request.POST:
                    user_email = request.POST['email_address']

                    if user_email:
                        # Validate user email if provided
                        if not regex_email.match(user_email):
                            form_errors += ['The e-mail address you provided does not appear to be valid.']

                # Dictionary of options which require a user email
                options_req_email = {'cb_preference_email_reminders': 'scheduled e-mail reminders',
                                     'cb_preference_email_updates': 'electronic communication regarding study outcomes',
                                     'cb_preference_prizes': 'monthly prize draws'}
                options_selected = set(options_req_email.keys()).intersection(set(request.POST.keys()))
                if options_selected and not user_email:
                    connector = " || "
                    plur_s = ""
                    if len(options_selected) > 1: plur_s = "s"
                    options_selected_str = connector.join([options_req_email[opt] for opt in options_selected])
                    num_conn = options_selected_str.count(connector)
                    options_selected_str = options_selected_str.replace(connector, ", ", num_conn-1)
                    options_selected_str = options_selected_str.replace(connector, ", and ")

                    form_errors += ['You did not provide an e-mail address. An e-mail address is required since you selected the following option' + plur_s + ': ' + options_selected_str + "."]

                # - check that an email reminder frequency is specified, if reminders are requested
                if 'cb_preference_email_reminders' in request.POST and 'radio_email_reminders_freq' not in request.POST:
                    form_errors += ['You have not selected a frequency for the scheduled e-mail reminders.']


                if not form_errors:

                    # Record user email, if provided, and send a verification email
                    if user_email:
                        new_email_token = crypto.generate_confirmation_token(request.user.username + user_email)
                        confirmation_link = website_hostname + "/activate/" + new_email_token

                        emailText = "Welcome to " + global_passed_vars['website_name'] + "!\n\nThank you for registering an account.\n\nPlease click this link to confirm your email address:\n\n<a href=\"" + confirmation_link + "\">" + confirmation_link + "</a>\n\nIf the link above does not work, please copy and paste it into your browser's address bar.\n\nWhy am I verifying my email address? We value your privacy and want to make sure that you are the one who initiated this registration. If you received this email by mistake, you can make it all go away by simply ignoring it."

                        emailHtml = """<h2 style="Margin-top: 0;color: #44a8c7;font-weight: 700;font-size: 24px;Margin-bottom: 16px;font-family: Lato,sans-serif;line-height: 32px;text-align: center">Welcome to """ + global_passed_vars['website_name'] + """!</h2>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">Thank you for registering an account.</p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><strong>Please click this link to confirm your email address:</strong></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><u><a href=\"""" + confirmation_link + """\">""" + confirmation_link + """</a></u></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">If the link above does not work, please copy and paste it into your browser's address bar.</p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><strong>Why am I verifying my email address?</strong>\r\n We value your privacy and want to make sure that you are the one who initiated this registration. If you received this email by mistake, you can make it all go away by simply ignoring it.</p>\r\n"""

                        successFlag = emails.sendEmail(email_username, email_name, [user_email], [], [], global_passed_vars['website_name'] + " - Email Confirmation", emailText, emails.emailPre + emailHtml + emails.emailPost)

                        # Update database to keep a record of sent emails, if the mailer was successful
                        if successFlag:
                            s = Subject.objects.get(user_id=request.user.id)
                            Subject_Emails.objects.create(date_sent=datetime.datetime.now().date(), subject=s, email_from=email_username, email_to=user_email, email_type='email_confirmation')

                        User.objects.filter(id=request.user.id).update(email=user_email)
                        Subject.objects.filter(user_id=request.user.id).update(email_validated=0,email_token=new_email_token)

                    # Update consent details
                    Subject.objects.filter(user_id=request.user.id).update(date_consent_submitted=date_submitted)
                    if request.POST['radio_consent'] == 'alternate':
                        Subject.objects.filter(user_id=request.user.id).update(consent_alternate=1)

                    # Preference for allowing public release of collected data
                    if 'cb_preference_public_release' in request.POST:
                        Subject.objects.filter(user_id=request.user.id).update(preference_public_release=1)

                    # Preference for receiving email reminders about completing sessions
                    if 'cb_preference_email_reminders' in request.POST:
                        reminders_freq = request.POST['radio_email_reminders_freq']
                        Subject.objects.filter(user_id=request.user.id).update(preference_email_reminders=1,preference_email_reminders_freq=reminders_freq,email_reminders=user_email)

                    # Preference for receiving email updates about related future research/publications
                    if 'cb_preference_email_updates' in request.POST:
                        Subject.objects.filter(user_id=request.user.id).update(preference_email_updates=1,email_updates=user_email)

                    # Preference for participation in monthly prize draws
                    if 'cb_preference_prizes' in request.POST:
                        Subject.objects.filter(user_id=request.user.id).update(preference_prizes=1,email_prizes=user_email)

            elif form_type == 'demographic':

                # Perform form validation first
                selected_gender = ""
                if 'gender' not in request.POST:
                    form_errors += ['You did not specify your gender.']
                else:
                    selected_gender = Gender.objects.filter(gender_id=request.POST['gender'])
                    if selected_gender:
                        selected_gender = selected_gender[0]

                selected_dob = ""
                if 'dob' not in request.POST or not request.POST['dob']:
                    form_errors += ['You did not specify your date of birth.']
                else:
                    selected_dob = request.POST['dob']
                    if not regex_date.match(selected_dob):
                        form_errors += ['The date of birth you specified is invalid (please enter in the format YYYY-MM-DD).']
                    else:
                        d1 = datetime.datetime.strptime(selected_dob, date_format)
                        d2 = datetime.datetime(d1.year + age_limit, d1.month, d1.day)
                        today = datetime.datetime.now()
                        delta = today - d2
                        if delta.days < 0:
                            form_errors += ['To participate in this study you must be at least 18 years of age.']

                if 'ethnicity' not in request.POST:
                    form_errors += ['You did not specify your ethnicity.']
                else:
                    response_ethnicity = request.POST.getlist('ethnicity')
                    for i in range(len(response_ethnicity)):
                        selected_ethnicity = Ethnicity.objects.filter(ethnicity_id=response_ethnicity[i])
                        if not selected_ethnicity:
                            form_errors += ['You have specified an invalid category for ethnicity.']


                # Get the fluency for each of the languages specified
                if 'language_other' in request.POST:
                    response_languages_other = request.POST.getlist('language_other')
                    for i in range(len(response_languages_other)):
                        if 'other_fluency_' + str(i+1) not in request.POST:
                            form_languages_other_fluency += [""]
                        else:
                            form_languages_other_fluency += [request.POST['other_fluency_' + str(i+1)]]


                if 'language' not in request.POST and ('language_other' not in request.POST or not [x for x in request.POST.getlist('language_other') if x]):
                    form_errors += ['You did not specify any languages you can communicate in.']
                else:
                    # Check that English has been selected as a spoken language
                    # Find ID of English language in db and compare to form inputs
                    response_languages = request.POST.getlist('language')

                    required_lang = "English"
                    english_lang = Language.objects.filter(name=required_lang)[0].language_id
                    if str(english_lang) not in response_languages:
                        form_errors += ['You did not specify any language proficiency in ' + required_lang + '. This is mandatory for participation, since this website is only available in ' + required_lang + '.']
                    else:
                        for i in range(len(response_languages)):
                            # - check that the selected languages are valid
                            selected_language = Language.objects.filter(language_id=response_languages[i])
                            if not selected_language:
                                form_errors += ['The language you have selected (' + str(response_languages[i]) + ') is invalid.']
                            else:
                                selected_language = selected_language[0]
                                # - check that level of fluency has been selected for each language
                                if 'language_fluency_' + str(response_languages[i]) not in request.POST:
                                    form_errors += ['You did not specify your level of fluency in ' + selected_language.name + '.']
                                    form_languages_fluency += [""]
                                else:
                                    form_languages_fluency += [request.POST['language_fluency_' + str(response_languages[i])] ]

                        response_languages_other = request.POST.getlist('language_other')
                        for i in range(len(response_languages_other)):
                            if response_languages_other[i]:
                                # - check that the selected languages are valid
                                selected_language = Language.objects.filter(language_id=response_languages_other[i])
                                if not selected_language:
                                    form_errors += ['The language you have selected (' + str(response_languages_other[i]) + ') is invalid.']
                                else:
                                    selected_language = selected_language[0]
                                    # - check that level of fluency has been selected for each language
                                    if 'other_fluency_' + str(i+1) not in request.POST:
                                        form_errors += ['You did not specify your level of fluency in ' + selected_language.name + '.']

                if 'education_level' not in request.POST:
                    form_errors += ['You did not specify your education level.']

                if 'dementia_med' not in request.POST:
                    form_errors += ['You did not specify whether you are currently take any medications for dementia.']

                if 'smoking' not in request.POST:
                    form_errors += ['You did not specify whether you are a regular smoker.']

                response_country_origin = ""
                if 'country_origin' not in request.POST or not request.POST['country_origin']:
                    form_errors += ['You did not specify the country you were born in.']
                else:
                    response_country_origin = Country.objects.filter(country_id=request.POST['country_origin'])
                    if not response_country_origin:
                        form_errors += ['You specified an invalid country of birth.']
                    else:
                        response_country_origin = response_country_origin[0]

                response_country_res = ""
                if 'country_res' not in request.POST or not request.POST['country_res']:
                    form_errors += ['You did not specify the country you currently reside in.']
                else:
                    response_country_res = Country.objects.filter(country_id=request.POST['country_res'])
                    if not response_country_res:
                        form_errors += ['You specified an invalid country of residence.']
                    else:
                        response_country_res = response_country_res[0]


                if not form_errors:
                    # Gender
                    Subject.objects.filter(user_id=request.user.id).update(gender=selected_gender)
                    gender_name = None
                    subject = Subject.objects.filter(user_id=request.user.id)
                    if subject:
                        subject = subject[0]
                    if 'gender_detail_o' in request.POST:
                        gender_name = request.POST['gender_detail_o']

                    subject_gender_exists = Subject_Gender.objects.filter(subject=subject, gender_id=selected_gender.gender_id)
                    if not subject_gender_exists:
                        Subject_Gender.objects.create(subject=subject,
                                                      gender_id=selected_gender.gender_id,
                                                      gender_name=gender_name)

                    # DOB
                    Subject.objects.filter(user_id=request.user.id).update(dob=selected_dob)

                    # Ethnicity
                    response_ethnicity = request.POST.getlist('ethnicity')
                    for i in range(len(response_ethnicity)):
                        selected_ethnicity = Ethnicity.objects.get(ethnicity_id=response_ethnicity[i])
                        subject = Subject.objects.filter(user_id=request.user.id)
                        if subject:
                            subject = subject[0]

                        ethnicity_exists = Subject_Ethnicity.objects.filter(subject=subject, ethnicity=selected_ethnicity)
                        if not ethnicity_exists:
                            Subject_Ethnicity.objects.create(subject=subject, ethnicity=selected_ethnicity)

                    # Languages
                    if 'language' in request.POST:
                        response_languages = request.POST.getlist('language')
                        for i in range(len(response_languages)):

                            selected_language = Language.objects.get(language_id=response_languages[i])
                            subject = Subject.objects.filter(user_id=request.user.id)
                            if subject:
                                subject = subject[0]

                            lang_exists = Subject_Language.objects.filter(subject=subject, language=selected_language)

                            lang_level = Language_Level.objects.filter(language_level_id=request.POST['language_fluency_' + str(response_languages[i])])
                            if lang_level:
                                lang_level = lang_level[0]

                            if not lang_exists:
                                Subject_Language.objects.create(subject=subject, language=selected_language, level=lang_level)
                            else:
                                Subject_Language.objects.filter(subject=subject, language=selected_language).update(level=lang_level)

                    if 'language_other' in request.POST:
                        response_languages = request.POST.getlist('language_other')
                        for i in range(len(response_languages)):

                            sel_response_language = response_languages[i]
                            if sel_response_language:
                                selected_language = Language.objects.get(language_id=sel_response_language)
                                subject = Subject.objects.filter(user_id=request.user.id)
                                if subject:
                                    subject = subject[0]

                                lang_exists = Subject_Language.objects.filter(subject=subject, language=selected_language)

                                lang_level = None
                                lang_level = Language_Level.objects.filter(language_level_id=request.POST['other_fluency_' + str(i+1)])
                                if lang_level:
                                    lang_level = lang_level[0]

                                if not lang_exists:
                                    Subject_Language.objects.create(subject=subject, language=selected_language, level=lang_level)
                                else:
                                    Subject_Language.objects.filter(subject=subject, language=selected_language).update(level=lang_level)


                    # Education level
                    response_education_level = request.POST['education_level']
                    selected_education_level = Education_Level.objects.filter(education_level_id=response_education_level)
                    if selected_education_level:
                        selected_education_level = selected_education_level[0]
                        Subject.objects.filter(user_id=request.user.id).update(education_level=selected_education_level)

                    # Dementia type
                    if 'dementia_type' in request.POST:
                        response_dementia_type = request.POST.getlist('dementia_type')
                        for i in range(len(response_dementia_type)):
                            selected_dementia_type = Dementia_Type.objects.filter(dementia_type_id=response_dementia_type[i])
                            selected_dementia_name = ""
                            if selected_dementia_type:
                                selected_dementia_type = selected_dementia_type[0]
                                if selected_dementia_type.requires_detail:
                                    if 'dementia_type_detail_' + str(response_dementia_type[i]) in request.POST:
                                        selected_dementia_name = request.POST['dementia_type_detail_' + str(response_dementia_type[i])]

                            subject = Subject.objects.filter(user_id=request.user.id)
                            if subject:
                                subject = subject[0]

                            dementia_type_exists = Subject_Dementia_Type.objects.filter(subject=subject, dementia_type_id=selected_dementia_type.dementia_type_id)
                            if not dementia_type_exists:
                                Subject_Dementia_Type.objects.create(subject=subject, dementia_type_id=selected_dementia_type.dementia_type_id, dementia_type_name=selected_dementia_name)

                    # Dementia meds
                    response_dementia_med = request.POST['dementia_med']
                    map_response_to_id = { 'yes': 1, 'no': 0}
                    if response_dementia_med in map_response_to_id:
                        response_dementia_med_id = map_response_to_id[response_dementia_med]
                        Subject.objects.filter(user_id=request.user.id).update(dementia_med=response_dementia_med_id)

                    # Smoking
                    response_smoking = request.POST['smoking']
                    map_response_to_id = { 'yes': 1, 'no': 0}
                    if response_smoking in map_response_to_id:
                        response_smoking_id = map_response_to_id[response_smoking]
                        Subject.objects.filter(user_id=request.user.id).update(smoker_recent=response_smoking_id)

                    # Country of origin
                    Subject.objects.filter(user_id=request.user.id).update(origin_country=response_country_origin)

                    # Country of residence
                    Subject.objects.filter(user_id=request.user.id).update(residence_country=response_country_res)

                    # Set the demographic flag to 1
                    Subject.objects.filter(user_id=request.user.id).update(date_demographics_submitted=date_submitted)

            elif form_type == 'delete_session':
                session_id = request.POST['session_id']
                session_id_check = request.POST['session_id_check']
                if session_id_check == session_id:
                    session_deleted = delete_session(session_id)
                else:
                    session_deleted = False

        # Assume that every authenticated user exists in subject. If they don't, add them with the appropriate ID, and all flags initialized to null/false.
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
        else:
            date_submitted = datetime.datetime.now()
            subject = Subject.objects.create(user_id=request.user.id, date_created=date_submitted, consent_alternate=0, email_validated=0, preference_email_reminders=0, preference_email_updates=0, preference_public_release=0, preference_prizes=0)

        # If first time logging in, display Consent Form, and ask for consent
        consent_submitted = subject.date_consent_submitted
        demographic_submitted = subject.date_demographics_submitted

        today = datetime.datetime.now().date()
        subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)
        if subject_bundle:
            subject_bundle = subject_bundle[0]

        # Demographic survey options/dropdowns
        if not demographic_submitted:
            gender_options = Gender.objects.all().order_by('ranking')
            language_options = Language.objects.all().exclude(is_official=0).order_by('name')
            language_other = Language.objects.all().exclude(is_official=1).order_by('name')
            language_fluency_options = Language_Level.objects.all().order_by('ranking')
            ethnicity_options = Ethnicity.objects.all().order_by('ranking')
            education_options = Education_Level.objects.all().order_by('-ranking')
            dementia_options = Dementia_Type.objects.all().order_by('ranking')
            country_res_options = Country.objects.all().order_by('name')

        # For the currently logged on user who has completed both consent and demographic forms, populate the index/dashboard
        # page with their previously completed and active sessions, and any notifications
        if consent_submitted and demographic_submitted:
            # Only show website sessions in the website interface
            completed_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=False).order_by('-start_date')
            active_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=True).order_by('-start_date')

            # Filter active sessions over the phone
            active_sessions_phone = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=True, session_type__name='phone')
            if active_sessions_phone:
                start_new_phone_session = False

            # Fetch all notifications that are active and have not been dismissed by the user
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = notify.get_active_new(subject)

            # Check if the user has not submitted a usability survey yet
            existing_survey = Subject_UsabilitySurvey.objects.filter(subject=subject, date_completed__isnull=False)
            if not existing_survey:
                usabilitysurvey_notsubmitted = True

            # Check if the user is associated with any active bundles
            today = datetime.datetime.now().date()
            subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)
            if subject_bundle:
                subject_bundle = subject_bundle[0]

                if subject_bundle.bundle.name_id == 'uhn_web' or subject_bundle.bundle.name_id == 'uhn_phone':
                    cutoff_date = today + datetime.timedelta(days=1)

                    if subject_bundle.bundle.name_id == 'uhn_web':

                        completed_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=False, session_type__name='website').order_by('start_date')
                        active_sessions = Session.objects.filter(start_date__lte=cutoff_date, subject__user_id=request.user.id, end_date__isnull=True, session_type__name='website').order_by('start_date')
                        pending_sessions = Session.objects.filter(start_date__gt=cutoff_date, subject__user_id=request.user.id, end_date__isnull=True, session_type__name='website').order_by('start_date')
                    else:
                        completed_sessions = Session.objects.filter(subject__user_id=request.user.id, end_date__isnull=False, session_type__name='phone').order_by('start_date')
                        active_sessions = Session.objects.filter(start_date__lte=cutoff_date, subject__user_id=request.user.id, end_date__isnull=True, session_type__name='phone').order_by('start_date')
                        pending_sessions = Session.objects.filter(start_date__gt=cutoff_date, subject__user_id=request.user.id, end_date__isnull=True, session_type__name='phone').order_by('start_date')

                    # Get percentage of completed tasks for active_sessions
                    percentage_completed = []
                    for i, session in enumerate(active_sessions):
                        session_id = session.session_id
                        num_current_task = Session_Task.objects.filter(session=session,date_completed__isnull=False).count()
                        num_tasks = Session_Task.objects.filter(session=session).count()
                        percentage_completed.append(min(100,round(num_current_task*100.0/num_tasks)))

                    num_completed_sessions = len(completed_sessions)
                    num_active_sessions = len(active_sessions)
                    num_pending_sessions = len(pending_sessions)

                    completed_sessions = zip(completed_sessions, range(1, num_completed_sessions + 1))
                    active_sessions = zip(active_sessions, percentage_completed, range(num_completed_sessions + 1, num_completed_sessions + num_active_sessions + 1))
                    pending_sessions = zip(pending_sessions, range(num_completed_sessions + num_active_sessions + 1, num_pending_sessions + num_active_sessions + num_completed_sessions + 1))

            else:
                # If the URL contains a bundle association, then create it if it doesn't already exist.
                # A user is assumed to be a part of one bundle at a time only.
                # Validate the passed in bundle parameters:
                bundle_exists = False
                bundle_valid = False
                if bundle_id and bundle_token and bundle_id.isdigit():
                    bundle_exists = Bundle.objects.filter(bundle_id=bundle_id)
                    if bundle_exists:
                        bundle_exists = bundle_exists[0]
                        if bundle_exists.bundle_token == bundle_token:
                            bundle_valid = True

                # If the passed in bundle parameter is valid, then assign the logged in user
                # on this page to the relevant task bundle, if they are not already assigned
                if bundle_exists and bundle_valid:
                    subj_bundle_token = crypto.generate_confirmation_token(str(subject.user_id) + str(bundle_exists.bundle_id) + str(bundle_exists.completion_req_sessions))
                    new_subject_bundle = Subject_Bundle.objects.create(subject=subject, bundle=bundle_exists, active_startdate=today, active_enddate=bundle_exists.active_enddate, completion_token=subj_bundle_token, completion_req_sessions=bundle_exists.completion_req_sessions)

    dict_language = {}
    dict_language_other = {}

    form_languages = [int(sel_lang) for sel_lang in request.POST.getlist('language') ]
    form_languages_other = [int(sel_lang) for sel_lang in request.POST.getlist('language_other') if sel_lang ]

    for i in range(len(form_languages)):
        if i < len(form_languages_fluency) and i >= 0:
            dict_language[form_languages[i]] = form_languages_fluency[i]
        else:
            dict_language[form_languages[i]] = ""

    for i in range(len(form_languages_other)):
        if i < len(form_languages_other_fluency) and i >= 0:
            dict_language_other[form_languages_other[i]] = form_languages_other_fluency[i]
        else:
            dict_language_other[form_languages_other[i]] = ""

    # , 'form_languages': form_languages, 'form_languages_other': form_languages_other, 'form_languages_fluency': form_languages_fluency
    passed_vars = {'is_authenticated': is_authenticated, 'dict_language': dict_language,
                   'dict_language_other': dict_language_other, 'consent_submitted': consent_submitted,
                   'demographic_submitted': demographic_submitted, 'usabilitysurvey_notsubmitted': usabilitysurvey_notsubmitted,
                   'form_values': request.POST, 'form_languages_other_fluency': form_languages_other_fluency,
                   'form_ethnicity': [int(sel_eth) for sel_eth in request.POST.getlist('ethnicity')],
                   'form_errors': form_errors, 'completed_sessions': completed_sessions, 'active_sessions': active_sessions,
                   'active_notifications': active_notifications, 'user': request.user, 'gender_options': gender_options,
                   'language_options': language_options, 'language_other': language_other,
                   'language_fluency_options': language_fluency_options, 'ethnicity_options': ethnicity_options,
                   'education_options': education_options, 'dementia_options': dementia_options,
                   'country_res_options': country_res_options, 'subject_bundle': subject_bundle,
                   'pending_sessions': pending_sessions, 'user_id': user_id, 'phone_pin': phone_pin,
                   'start_new_phone_session': start_new_phone_session }
    passed_vars.update(global_passed_vars)
    return render_to_response('datacollector/main.html', passed_vars, context_instance=RequestContext(request))

def login(request):

    # If there is a currently logged in user, just redirect to home page
    if request.user.is_authenticated():

        # Check if the user is associated with any active bundles
        subject = Subject.objects.get(user_id=request.user.id)
        today = datetime.datetime.now().date()
        subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)
        if subject_bundle:
            if subject_bundle[0].bundle.name_id == 'uhn_web' or subject_bundle[0].bundle.name_id == 'uhn_phone':
                return HttpResponseRedirect(uhn_website_root)
            elif subject_bundle[0].bundle.name_id == 'oise':
                return HttpResponseRedirect(OISE_WEBSITE_ROOT)
            elif subject_bundle[0].bundle.name_id == 'wch_web' or subject_bundle[0].bundle.name_id == 'wch_phone':
                return HttpResponseRedirect(WCH_WEBSITE_ROOT)

        return HttpResponseRedirect(website_root)

    # If the form has been submitted, validate the data and
    errors = []
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    auth_login(request,user)

                    # Check if the user is associated with any active bundles
                    subject = Subject.objects.get(user_id=user.id)
                    today = datetime.datetime.now().date()
                    subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)
                    if subject_bundle:
                        if subject_bundle[0].bundle.name_id == 'uhn_web' or subject_bundle[0].bundle.name_id == 'uhn_phone':
                            return HttpResponseRedirect(uhn_website_root)
                        elif subject_bundle[0].bundle.name_id == 'oise':
                            return HttpResponseRedirect(OISE_WEBSITE_ROOT)
                        elif subject_bundle[0].bundle.name_id == 'wch_web' or subject_bundle[0].bundle.name_id == 'wch_phone':
                            return HttpResponseRedirect(WCH_WEBSITE_ROOT)

                    # Success: redirect to the home page
                    return HttpResponseRedirect(website_root)
                else:
                    # Return a 'disabled account' error message
                    errors.append("Your account is currently disabled. Please contact the website administrator for assistance.")
            else:
                # Return an 'invalid login' error message
                errors.append("Invalid login credentials, please try again.")
    else:
        form = LoginForm()

    passed_vars = {'form': form, 'errors': errors}
    passed_vars.update(global_passed_vars)
    return render_to_response('datacollector/login.html', passed_vars, context_instance=RequestContext(request))


def logout(request):
    subject = Subject.objects.get(user_id=request.user.id)
    auth_logout(request)

    today = datetime.datetime.now().date()
    subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)
    if subject_bundle:
        if subject_bundle[0].bundle.name_id == 'uhn_web' or subject_bundle[0].bundle.name_id == 'uhn_phone':
            return HttpResponseRedirect(uhn_website_root)
        elif subject_bundle[0].bundle.name_id == 'oise':
            return HttpResponseRedirect(OISE_WEBSITE_ROOT)
        elif subject_bundle[0].bundle.name_id == 'wch_web' or subject_bundle[0].bundle.name_id == 'wch_phone':
            return HttpResponseRedirect(WCH_WEBSITE_ROOT)

    return HttpResponseRedirect(website_root)


def register(request):
    '''
        Register new user on POST request or display registration page on GET request.
    '''

    bundle_id = None
    bundle_token = None
    get_querystring = ""
    if 'bid' in request.GET and 'bt' in request.GET:
        bundle_id = request.GET['bid']
        bundle_token = request.GET['bt']
        get_querystring = "?bid=" + bundle_id + "&bt=" + bundle_token

    # If there is a currently logged in user, just redirect to home page
    if request.user.is_authenticated():

        # Check if the user is associated with any active bundles
        subject = Subject.objects.get(user_id=request.user.id)
        today = datetime.datetime.now().date()
        subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)
        if subject_bundle:
            if subject_bundle[0].bundle.name_id == 'uhn_web' or subject_bundle[0].bundle.name_id == 'uhn_phone':
                return HttpResponseRedirect(uhn_website_root)

        return HttpResponseRedirect(website_root + get_querystring)

    # If the form has been submitted, validate the data and login the user automatically
    errors = []
    today = datetime.datetime.now().date()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_user = form.save()

            # Generate a new PIN for the phone interface
            pin_length = 4
            random_pin = random.randint(0, 10**pin_length-1)
            phone_pin = str(random_pin).zfill(pin_length) # zero pad where necessary

            # Create a corresponding subject in the app
            new_subject = Subject.objects.create(user_id=new_user.id, date_created=datetime.datetime.now(), phone_pin=phone_pin)

            # Validate the passed in bundle parameters
            bundle_exists = False
            bundle_valid = False
            if 'bundle_id' in request.POST and 'bundle_token' in request.POST:
                bundle_id = request.POST['bundle_id']
                bundle_token = request.POST['bundle_token']
                if bundle_id and bundle_token and bundle_id.isdigit():
                    bundle_exists = Bundle.objects.filter(bundle_id=bundle_id)
                    if bundle_exists:
                        bundle_exists = bundle_exists[0]
                        if bundle_exists.bundle_token == bundle_token:
                            bundle_valid = True

            # If the passed in bundle parameter is valid, then assign the newly created user
            # on this page to the relevant task bundle
            if bundle_exists and bundle_valid:
                subj_bundle_token = crypto.generate_confirmation_token(str(new_subject.user_id) + str(bundle_exists.bundle_id) + str(bundle_exists.completion_req_sessions))
                new_subject_bundle = Subject_Bundle.objects.create(subject=new_subject, bundle=bundle_exists, active_startdate=today, active_enddate=bundle_exists.active_enddate, completion_token=subj_bundle_token, completion_req_sessions=bundle_exists.completion_req_sessions)

            # Automatically log the user in and redirect to index page
            new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            auth_login(request,new_user)

            # OISE-specific registration gets re-directed to the OISE index
            if bundle_exists and bundle_valid and bundle_id:
                bundle = Bundle.objects.get(bundle_id=bundle_id)
                if bundle.name_id == 'oise':

                    # Set consent_submitted to today
                    today = datetime.datetime.now().date()
                    Subject.objects.filter(user_id=new_user.id).update(date_consent_submitted=today)

                    return HttpResponseRedirect(OISE_WEBSITE_ROOT)
            return HttpResponseRedirect(website_root)
    else:
        form = UserCreationForm()

    passed_vars = {
        'form': form, \
        'bundle_id': bundle_id, \
        'bundle_token': bundle_token
    }
    passed_vars.update(global_passed_vars)

    return render_to_response('datacollector/register.html', \
                              passed_vars, \
                              context_instance=RequestContext(request))

def question(request, session_id, instance_id):
    passed_vars = {'session': session, 'subject': subject, 'task_instance': instance}
    passed_vars.update(global_passed_vars)
    return render_to_response('datacollector/question.html', passed_vars)


def startsession(request):
    # Begin a new session for the current user: set up the database tables,
    # the task instances and the response fields.

    if request.user.is_authenticated():

        subject = Subject.objects.get(user_id=request.user.id)

        today = datetime.datetime.now().date()
        subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)

        if subject_bundle:
            # Participants in the UHN study should not be able to create their own sessions
            if subject_bundle[0].bundle.bundle_id == UHN_WEB_BUNDLE_ID or subject_bundle[0].bundle.bundle_id == UHN_PHONE_BUNDLE_ID:
                return HttpResponseRedirect(uhn_website_root)

        session_type = Session_Type.objects.get(name='website')
        new_session = generate_session(subject, session_type)

        if subject_bundle and \
            subject_bundle[0].bundle.bundle_id == OISE_BUNDLE_ID:
            # Participants in the OISE study should be re-directed to the OISE-specific URL
            return HttpResponseRedirect(website_root + 'oise/session/' + \
                                        str(new_session.session_id))
        return HttpResponseRedirect(website_root + 'session/' + str(new_session.session_id))
    else:
        return HttpResponseRedirect(website_root)

def notfound(request):

    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False

    if request.user.is_authenticated():
        is_authenticated = True
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted

    passed_vars = {'user': request.user, 'is_authenticated': is_authenticated, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted}
    passed_vars.update(global_passed_vars)

    return render_to_response('datacollector/notfound.html', passed_vars, context_instance=RequestContext(request))

def activate(request, user_token):

    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    email_prevalidated = False
    email_validated = False
    email_address = ""
    active_notifications = []

    if request.user.is_authenticated():
        is_authenticated = True
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted

            # Fetch all notifications that are active and have not been dismissed by the user
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = notify.get_active_new(subject)

    # Determine if the token is valid
    s = Subject.objects.filter(email_token=user_token)
    if not s:
        return HttpResponseRedirect(website_root + "404")

    # Determine if user's email is already confirmed
    u = User.objects.filter(id=s[0].user_id)
    if u:
        email_address = u[0].email
        if s[0].email_validated:
            email_prevalidated = True
        else:
            s.update(email_validated=1)
            email_validated = True

    passed_vars = {'user': request.user, 'is_authenticated': is_authenticated, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications, 'email_prevalidated': email_prevalidated, 'email_validated': email_validated, 'email_address': email_address}
    passed_vars.update(global_passed_vars)

    return render_to_response('datacollector/activate.html', passed_vars, context_instance=RequestContext(request))


def session(request, session_id):

    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    active_notifications = []
    is_uhn_study = False

    if request.user.is_authenticated():

        is_authenticated = True
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted

            # Fetch all notifications that are active and have not been dismissed by the user
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = notify.get_active_new(subject)

        # Check if UHN study
        today = datetime.datetime.now().date()
        subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)
        if subject_bundle:
            subject_bundle = subject_bundle[0]
            if subject_bundle.bundle.name_id == 'uhn_web' or subject_bundle.bundle.name_id == 'uhn_phone':
                is_uhn_study = True

        session = Session.objects.filter(session_id=session_id)
        if session:
            session = session[0]

            # Update the date_last_session_access for the user (this drives reminder emails)
            date_access = datetime.datetime.now()
            Subject.objects.filter(user_id=request.user.id).update(date_last_session_access=date_access)

            # If the session is active, find the first unanswered task instance to display
            active_task = None
            active_instances = []
            serial_instances = False
            serial_startslide = ""
            active_session_task_id = None
            display_thankyou = False
            next_session_date = None

            # Get next session
            next_sessions = Session.objects.filter(subject_id=subject.user_id, end_date__isnull=True).order_by('start_date')
            if next_sessions:
                next_session_date = next_sessions[0].start_date

            # Initialize global vars for session page
            requires_audio = False
            existing_responses = False
            num_current_task = Session_Task.objects.filter(session=session,date_completed__isnull=False).count() + 1
            num_tasks = Session_Task.objects.filter(session=session).count()
            completed_date = session.end_date
            session_summary = ""

            if not session.end_date:

                # If session responses are submitted, perform validation. If validation passes, write them to the database and return a 'success' response to the AJAX script. If validation fails, return a 'fail' response to the AJAX script, along with the form errors found.
                if request.method == "POST":

                    form_errors = []
                    json_data = {}
                    json_data['status'] = 'fail'

                    active_task = Session_Task.objects.filter(session=session,date_completed__isnull=True).order_by('order')
                    if active_task:
                        active_task = active_task[0]

                        # Validate the form first
                        # Determine the order of the questions associated with this task (e.g., non-select questions have 'response' fields, whereas
                        # select questions have 'response_{instanceid}' fields).
                        active_task_questions = Session_Task_Instance_Value.objects.filter(session_task_instance__session_task=active_task, task_field__field_type__name='display')
                        form_responses = request.POST.getlist('response')
                        form_instances = request.POST.getlist('instanceid')
                        responses = copy.deepcopy(form_responses)
                        instances = copy.deepcopy(form_instances)
                        counter_question = 0
                        for question in active_task_questions:
                            question_response = Task_Field.objects.get(assoc=question.task_field)

                            next_instance = instances.pop(0)
                            if question_response.field_data_type.name == 'select' or question_response.field_data_type.name == 'audio' or (active_task.task_id == RIG_TASK_ID and is_uhn_study):
                                # If the associated response field is 'select' or 'audio', then there will be 'response_{instanceid}' fields
                                audio_label = 'response_audio_' + str(next_instance)
                                if not audio_label in request.POST:
                                    response_label = 'response_' + str(next_instance)
                                    if response_label in request.POST:
                                        next_response = request.POST[response_label]
                                        if not next_response:
                                            form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
                                        if not next_instance:
                                            form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
                                        else:
                                            instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)
                                            if not instance:
                                                form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
                                    else:
                                        form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
                            else:
                                # Otherwise, look for 'response' fields
                                next_response = responses.pop(0)
                                if not next_response:
                                    form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
                                if not next_instance:
                                    form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
                                else:
                                    instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)
                                    if not instance:
                                        form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
                            counter_question += 1


                        # Process any input, textarea (text), and multiselect responses
                        if not form_errors:
                            responses = copy.deepcopy(form_responses)
                            instances = copy.deepcopy(form_instances)

                            for question in active_task_questions:
                                question_response = Task_Field.objects.get(assoc=question.task_field)

                                next_instance = instances.pop(0)
                                if question_response.field_data_type.name == 'select' or question_response.field_data_type.name == 'audio' or (active_task.task_id == RIG_TASK_ID and is_uhn_study):
                                    # If the associated response field is 'select' or 'audio', then there will be 'response_{instanceid}' fields
                                    audio_label = 'response_audio_' + str(next_instance)
                                    if not audio_label in request.POST:
                                        response_label = 'response_' + str(next_instance)
                                        if response_label in request.POST:
                                            next_response = request.POST[response_label]
                                            instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)[0]

                                            # Find the response field type for this task
                                            response_data_type = Task_Field.objects.filter(task=instance.session_task.task,field_type__name='input')[0].field_data_type

                                            if response_data_type == 'select':
                                                Session_Response.objects.filter(session_task_instance=instance).update(value_text=next_response,date_completed=datetime.datetime.now())
                                            else:
                                                Session_Response.objects.filter(session_task_instance=instance).update(value_text=next_response,date_completed=datetime.datetime.now())
                                else:
                                    # Otherwise, look for 'response' fields
                                    next_response = responses.pop(0)
                                    instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)[0]

                                    # Find the response field type for this task
                                    response_data_type = Task_Field.objects.filter(task=instance.session_task.task,field_type__name='input')[0].field_data_type

                                    # Update the appropriate entry in the database (NB: 'audio' responses are not handled here; they are saved to database as soon as they are recorded, to avoid loss of data)
                                    if response_data_type == 'multiselect':
                                        Session_Response.objects.filter(session_task_instance=instance).update(value_multiselect=next_response,date_completed=datetime.datetime.now())
                                    else:
                                        Session_Response.objects.filter(session_task_instance=instance).update(value_text=next_response,date_completed=datetime.datetime.now())


                            # Mark the task as submitted
                            Session_Task.objects.filter(session=session,task=active_task.task).update(date_completed=datetime.datetime.now())

                            json_data['status'] = 'success'

                    if form_errors:
                        json_data['error'] = [dict(msg=x) for x in form_errors]
                    return HttpResponse(json.dumps(json_data))

                num_current_task = Session_Task.objects.filter(session=session,date_completed__isnull=False).count() + 1
                num_tasks = Session_Task.objects.filter(session=session).count()
                active_task = Session_Task.objects.filter(session=session,date_completed__isnull=True).order_by('order')
                if not active_task:
                    # All tasks in the current session have been completed - mark the session as complete with an end date stamp, and display acknowledgement. Display summary. Trigger notification generation.
                    display_thankyou = True

                    completed_date = datetime.datetime.now()
                    Session.objects.filter(session_id=session.session_id).update(end_date=completed_date)

                    summary_tasks = Session_Task.objects.filter(session=session).order_by('order')
                    counter = 1
                    for next_task in summary_tasks:
                        next_task_instances = Session_Task_Instance.objects.filter(session_task=next_task).aggregate(count_instances=Count('session_task_instance_id'))
                        session_summary += "<tr><td>" + str(counter) + "</td><td>" + next_task.task.name + "</td><td>" + str(next_task_instances['count_instances']) + "</td></tr>"
                        counter += 1

                    # Trigger notifications that are linked to session completion
                    notify.generate_notifications(subject, "onSessionComplete")

                else:
                    active_session_task_id = active_task[0].session_task_id
                    active_task = active_task[0].task
                    responses_dict = {}
                    active_task_responses = Session_Response.objects.filter(session_task_instance__session_task__session=session, session_task_instance__session_task__task=active_task).order_by('session_task_instance__session_task__order')
                    for response in active_task_responses:
                        if response.session_task_instance not in responses_dict:
                            responses_dict[response.session_task_instance] = response

                    active_task_instance_values = Session_Task_Instance_Value.objects.filter(session_task_instance__session_task__session=session, session_task_instance__session_task__task=active_task, task_field__field_type__name='display').order_by('session_task_instance','task_field')

                    # Add an attribute for each task, defining it as serial or not
                    if active_task.name_id == "stroop":
                        serial_instances = True
                        first_instance_id = str(active_task_instance_values[0].session_task_instance.session_task_instance_id)
                        serial_startslide = "<div class='space-bottom-med space-top-med stroop-slide'><div style='font-size: 72px;'>&nbsp;</div><button type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: stroopTaskBegin(this);'>Start</button><input class='form-field' type='hidden' id='response_audio_" + first_instance_id + "' name='response_audio_" + first_instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + first_instance_id + "' /></div>"
                        requires_audio = True

                    count_inst = 0
                    for instance_value in active_task_instance_values:

                        # Determine how to display the value based on the field type
                        display_field = ""
                        response_field = ""
                        field_data_type = instance_value.task_field.field_data_type.name

                        # Construct style attributes string from the specified field data attributes
                        field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=instance_value.task_field)
                        style_attributes = ";".join([str(attr.name) + ": " + str(attr.value) for attr in field_data_attributes])

                        session_task_instance = instance_value.session_task_instance
                        instance_id = str(instance_value.session_task_instance.session_task_instance_id)

                        if field_data_type == "text":
                            display_field = instance_value.value.replace('\n', '<br>')
                        elif field_data_type == "text_well":
                            display_field = "<div class='well well-lg space-bottom-small'>" + instance_value.value.replace('\n', '<br>') + "</div>"
                        elif field_data_type == "image":
                            display_field = "<img src='" + STATIC_URL + "img/" + instance_value.value + "' style=\"" + style_attributes + "\" />"
                        elif field_data_type == "text_withblanks":
                            display_field = (instance_value.value).replace("[BLANK]", "<input class='form-field' name='response' type='text' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />")
                        elif field_data_type == "timer_rig":

                            # Parse out the duration of the timer
                            timer_duration = re.compile(r"\[timer_([0-9]+)(min|sec)\]")
                            instance_duration = timer_duration.findall(instance_value.value)
                            if instance_duration:
                                dur_sec = instance_duration[0][0]
                                dur_unit = instance_duration[0][1]
                                if dur_unit is 'min':
                                    dur_sec = dur_sec * 60
                            else:
                                # Default duration
                                dur_sec = 60


                            # For UHN study, record RIG answers as audio
                            if is_uhn_study:
                                requires_audio = True

                                # TODO: Use regex or update in DB
                                display_value = instance_value.value
                                display_value = display_value.replace('write down', 'say')

                                display_value = display_value.replace('in the box below', 'that come to mind randomly')

                                display_value = display_value.replace('Separate them with commas. Keep writing for 1 minute', 'Keep talking for 1 minute')
                                display_value = display_value.replace('Separate the names with commas. Keep writing for 1 minute', 'Keep talking for 1 minute')
                                display_value = display_value.replace('Separate the letters with commas. Keep writing for 1 minute', 'Keep talking for 1 minute')
                                display_value = display_value.replace('Separate the numbers with commas. Keep writing for 1 minute', 'Keep talking for 1 minute')

                                display_field = re.sub(timer_duration, "<br /><br />", display_value)
                                display_field += '''<div class='timer_display' id='timer_display_%s'>01:00</div>
                                                    <input type='hidden' id='timer_val_%s' value='%s' />
                                                    <input class='form-field' name='instanceid' type='hidden' value='%s' />''' % (instance_id, instance_id, dur_sec, instance_id)

                                response_field = ""
                                response_field += "<p id='record-btn_" + instance_id + "'"
                                response_field += "><input id='btn_recording_" + instance_id + "' type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: toggleRecordingRig(this); startTimerRigAudio(this, " + instance_id + ");' value='Start recording'>&nbsp;<span class='invisible' id='status_recording_" + instance_id + "'><img src='" + STATIC_URL + "img/ajax_loader.gif' /> <span id='status_recording_" + instance_id + "_msg'></span></span><input class='form-field' type='hidden' id='response_audio_" + instance_id + "' name='response_audio_" + instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' /></p>"

                            else:
                                display_field = re.sub(timer_duration, "<br /><br /><button type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: startTimerRig(this, " + instance_id + ");'>Start Timer</button><br />", instance_value.value)
                                # Associated textarea where the user will type out the RIG response
                                display_field += "<div class='timer_display' id='timer_display_" + instance_id + "'>01:00</div><input type='hidden' id='timer_val_" + instance_id + "' value='" + dur_sec + "' /><textarea class='form-control form-field input-disabled' name='response' readonly='readonly' style=\"" + style_attributes + "\"></textarea><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"


                        elif field_data_type == "text_newlines":
                            sents = instance_value.value.split(" || ")
                            regex_nonalpha = re.compile(r"^[^a-zA-Z0-9]+$")
                            display_field = "<br>".join([sent[0].lower() + sent[1:] for sent in sents if not regex_nonalpha.findall(sent)])
                        elif field_data_type == "text_stroop":
                            # Each instance should be displayed on its own, serially, with JS 'next' buttons in between
                            # HTML/JS: Display each instance in a div with class 'invisible', and add a JS function on 'next' button click
                            # which would hide the current div and display the next. If there is no next div, stop the audio recording
                            # and make the submit button active.

                            # Since this is a Stroop task, determine the colour in which the word stimulus should be displayed
                            word_stimulus,colour_stimulus = instance_value.value.split("|")
                            colour_hex = colour_lookup[colour_stimulus]

                            append_audio_response = ""
                            if count_inst+1 < len(active_task_instance_values):
                                next_instance_id = str(active_task_instance_values[count_inst+1].session_task_instance.session_task_instance_id)
                                if next_instance_id:
                                    append_audio_response = "<div class='invisible status_recording' style='margin-top: 5px;'><img src='" + STATIC_URL + "img/ajax_loader.gif' /> <span class='status_recording_msg small'></div><input class='form-field' type='hidden' id='response_audio_" + next_instance_id + "' name='response_audio_" + next_instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + next_instance_id + "' />"

                            serial_startslide += "<div class='invisible stroop-slide'><div style='font-size: 72px; font-weight: bold; color: #" + colour_hex + ";'>" + word_stimulus.upper() + "</div><button type='button' class='btn btn-success btn-med btn-fixedwidth recording' onClick='javascript: stroopTaskNextItem(this);'>Next</button>" + append_audio_response + "</div>"
                        else:
                            display_field = instance_value.value.replace('\n', '<br>')


                        # Find associated response field data type

                        if not instance_value.task_field.embedded_response:
                            response_field = Session_Response.objects.filter(session_task_instance=instance_value.session_task_instance)[0]
                            if response_field.date_completed:
                                existing_responses = True

                            input_field = Task_Field.objects.get(task=active_task, field_type__name='input', assoc=instance_value.task_field)
                            field_data_type = input_field.field_data_type.name

                            # Construct style attributes string from the specified field data attributes
                            field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=input_field)
                            style_attributes = ";".join([str(attr.name) + ": " + str(attr.value) for attr in field_data_attributes])

                            # regex for field data type 'scale' (scale_{from}_{to})
                            regex_scale = re.compile(r'scale\_([0-9]+)\_([0-9]+)')

                            if field_data_type == "multiselect":
                                existing_value = ""
                                if response_field.value_text:
                                    existing_value = response_field.value_text
                                response_field = "<input class='form-field form-control' name='response' type='text' value='" + existing_value + "'><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
                            elif field_data_type == "text":
                                existing_value = ""
                                if response_field.value_text:
                                    existing_value = response_field.value_text
                                response_field = "<input class='form-field form-control' name='response' type='text' value='" + existing_value + "' style=\"" + style_attributes + "\"><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
                            elif field_data_type == "textarea":
                                existing_value = ""
                                if response_field.value_text:
                                    existing_value = response_field.value_text
                                response_field = "<textarea class='form-field form-control' name='response' style=\"" + style_attributes + "\">" + existing_value + "</textarea><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
                            elif field_data_type == "audio":
                                requires_audio = True

                                # If the display field is to be kept visible during the audio the subject provides, keep it visible and directly show a recording button
                                keep_visible = instance_value.task_field.keep_visible
                                response_field = ""
                                if not keep_visible:
                                    response_field += "<p><input class='btn btn-primary btn-med btn-fixedwidth' type='button' onClick='javascript: hideDisplay(this);' value='Continue'></p>"
                                response_field += "<p id='record-btn_" + instance_id + "'"
                                if not keep_visible:
                                    response_field += " class='invisible'"
                                response_field += "><input id='btn_recording_" + instance_id + "' type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: toggleRecording(this);' value='Start recording'>&nbsp;<span class='invisible' id='status_recording_" + instance_id + "'><img src='" + STATIC_URL + "img/ajax_loader.gif' /> <span id='status_recording_" + instance_id + "_msg'></span></span><input class='form-field' type='hidden' id='response_audio_" + instance_id + "' name='response_audio_" + instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' /></p>"

                            elif field_data_type == "select":
                                existing_value = ""
                                if response_field.value_text:
                                    existing_value = response_field.value_text
                                response_field = ""

                                # Get associated values for the select options.
                                sel_options = Session_Task_Instance_Value.objects.filter(session_task_instance=instance_value.session_task_instance,task_field__field_type__name='input').order_by('session_task_instance_value_id')

                                for sel_option in sel_options:
                                    response_field += "<div class='radio'>"
                                    response_field += "<label><input type='radio' class='form-field' name='response_" + instance_id + "' value='" + sel_option.value + "'"

                                    # Mark any previously-submitted responses as selected
                                    if existing_value == sel_option.value:
                                        response_field += " selected='selected'"

                                    response_field += "> " + sel_option.value_display + "</label>"
                                    response_field += "</div>"

                                response_field += "<input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"

                            elif regex_scale.findall(field_data_type):
                                matches = regex_scale.findall(field_data_type)
                                scale_start = matches[0][0]
                                scale_end = matches[0][1]

                                response_field = "<div class='row'><div class='col-xs-6'><div class='scale_" + str(scale_start) + "_" + str(scale_end) + "' style=\"" + style_attributes + "\"></div><div class='scale_display' style='font-size: 20px;'></div><input class='form-field' name='response' type='hidden' value='' /></div></div><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"

                        # For picture description, display 'Record' button before image
                        if active_task.name_id == 'picture_description':
                            active_instances += [response_field + "<br/>" + display_field]
                        else:
                            active_instances += [display_field + "<br/>" + response_field]
                        count_inst += 1

            else:
                # The session has been completed. Display a summary.
                summary_tasks = Session_Task.objects.filter(session=session).order_by('order')
                counter = 1
                for next_task in summary_tasks:
                    next_task_instances = Session_Task_Instance.objects.filter(session_task=next_task).aggregate(count_instances=Count('session_task_instance_id'))
                    session_summary += "<tr><td>" + str(counter) + "</td><td>" + next_task.task.name + "</td><td>" + str(next_task_instances['count_instances']) + "</td></tr>"
                    counter += 1

            passed_vars = {
                'session': session, 'num_current_task': num_current_task, 'num_tasks': num_tasks,
                'percentage_completion': min(100,round(num_current_task*100.0/num_tasks)),
                'active_task': active_task, 'active_session_task_id': active_session_task_id,
                'serial_instances': serial_instances, 'serial_startslide': serial_startslide,
                'active_instances': active_instances, 'requires_audio': requires_audio,
                'existing_responses': existing_responses, 'completed_date': completed_date,
                'session_summary': session_summary, 'display_thankyou': display_thankyou,
                'user': request.user, 'is_authenticated': is_authenticated,
                'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted,
                'active_notifications': active_notifications, 'is_uhn_study': is_uhn_study,
                'next_session_date': next_session_date
            }
            passed_vars.update(global_passed_vars)

            return render_to_response('datacollector/session.html', passed_vars, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(website_root)
    else:
        return HttpResponseRedirect(website_root)


def results(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    # Get all associated responses from the database
    # TODO

    passed_vars = {'subject': subject}
    passed_vars.update(global_passed_vars)

    return render_to_response('datacollector/result.html', passed_vars, context_instance=RequestContext(request))

def survey_usability(request):
    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    active_notifications = []
    form_errors = []
    web_survey_completed = False
    phone_survey_completed = False

    phone_survey_type = Subject_UsabilitySurvey_Type.objects.get(name='phone').usabilitysurvey_type_id
    web_survey_type = Subject_UsabilitySurvey_Type.objects.get(name='web').usabilitysurvey_type_id

    if request.user.is_authenticated():
        is_authenticated = True
        date_completed = None
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted

            # Check if the user has not submitted a usability survey for the web yet
            existing_web_survey = Subject_UsabilitySurvey.objects.filter(subject=subject,
                                                                         date_completed__isnull=False,
                                                                         usabilitysurvey_type_id=web_survey_type)
            if not existing_web_survey:
                web_survey_completed = True

            # Check if the user has not submitted a usability survey for the phone yet
            existing_phone_survey = Subject_UsabilitySurvey.objects.filter(subject=subject,
                                                                           date_completed__isnull=False,
                                                                           usabilitysurvey_type_id=phone_survey_type)
            if not existing_phone_survey:
                phone_survey_completed = True

    passed_vars = {'is_authenticated': is_authenticated, 'consent_submitted': consent_submitted,
                   'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications,
                   'web_survey_completed': web_survey_completed, 'phone_survey_completed': phone_survey_completed}
    passed_vars.update(global_passed_vars)
    return render_to_response('datacollector/usabilitysurvey.html', passed_vars, context_instance=RequestContext(request))

def survey_usability_phone(request):
    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    active_notifications = []
    survey_date_completed = False
    form_errors = []
    is_wch_study = False

    # The HTML IDs/names of the questions in the survey template
    questions = {'radio': ['h1_phone', 'h2_phone', 'h3_phone',
                           'h4_phone', 'h5_phone', 'h6_phone',
                           'h7_phone', 'h8_phone',
                           'sat1_phone', 'sat2_phone',
                           'ease1_phone', 'ease2_phone', 'ease3_phone',
                           'ease4_phone', 'ease5_phone', 'ease6_phone',
                           'use1_phone', 'use2_phone'],
                 'textarea': ['prev_tests_phone', 'phone_vs_inperson',
                              'complaints_phone', 'phone_comm', 'phone_frustration',
                              't2m_phone_use', 'future_use_phone']
                }
    question_numbers = {'h1_phone': 1, 'h2_phone': 1, 'h3_phone': 1, 'h4_phone': 1,
                        'h5_phone': 1, 'h6_phone': 1, 'h7_phone': 1, 'h8_phone': 1,
                        'sat1_phone': 2, 'sat2_phone': 2,
                        'ease1_phone': 3, 'ease2_phone': 3, 'ease3_phone': 3,
                        'ease4_phone': 3, 'ease5_phone': 3, 'ease6_phone': 3,
                        'use1_phone': 4, 'use2_phone': 4,
                        'prev_tests_phone': 5,
                        'phone_vs_inperson': 6,
                        'complaints_phone': 7,
                        'phone_comm': 8,
                        'phone_frustration': 9,
                        't2m_phone_use': 10,
                        'future_use_phone': 11}
    question_order = ['h1_phone', 'h2_phone', 'h3_phone', 'h4_phone',
                      'h5_phone', 'h6_phone','h7_phone', 'h8_phone',
                      'sat1_phone', 'sat2_phone',
                      'ease1_phone', 'ease2_phone', 'ease3_phone',
                      'ease4_phone', 'ease5_phone', 'ease6_phone',
                      'use1_phone', 'use2_phone',
                      'prev_tests_phone', 'phone_vs_inperson',
                      'complaints_phone', 'phone_comm', 'phone_frustration',
                      't2m_phone_use', 'future_use_phone']

    phone_survey_type = Subject_UsabilitySurvey_Type.objects.get(name='phone').usabilitysurvey_type_id

    if request.user.is_authenticated():
        is_authenticated = True
        date_completed = None
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted

            # Fetch all notifications that are active and have not been dismissed by the user
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = notify.get_active_new(subject)

            # Check for associated bundle
            subject_bundle = Subject_Bundle.objects.filter(subject=subject)
            if subject_bundle:
                if subject_bundle[0].bundle.name_id == 'wch_web' or subject_bundle[0].bundle.name_id == 'wch_phone':
                    is_wch_study = True

            if request.method == "POST":
                # Check for missing responses
                for question_type in questions:
                    question_names = questions[question_type]
                    for n in question_names:
                        if n not in request.POST or not request.POST[n]:
                            form_errors += ['You did not provide a response to question #%d' % (question_numbers[n])]

                # Save the submitted survey responses if there are no errors
                if not form_errors:
                    date_completed = datetime.datetime.now()
                    for question_type in questions:
                        for n in questions[question_type]:
                            if n in request.POST and request.POST[n]:
                                response_id = request.POST[n]
                                question = request.POST['%s_question' % n]
                                key_response = '%s_%s_response' % (n, response_id)
                                if key_response in request.POST:
                                    response = request.POST[key_response]
                                else:
                                    response = response_id
                                Subject_UsabilitySurvey.objects.create(subject=subject,
                                                                       question_id=n,
                                                                       question=question,
                                                                       question_type=question_type,
                                                                       question_order=question_order.index(n),
                                                                       response_id=response_id,
                                                                       response=response,
                                                                       date_completed=date_completed,
                                                                       usabilitysurvey_type_id=phone_survey_type)
                    survey_date_completed = date_completed
                else:
                    # Sort the errors and unique only
                    form_errors = sorted(list(set(form_errors)))

            existing_survey = Subject_UsabilitySurvey.objects.filter(subject=subject,
                                                                     date_completed__isnull=False,
                                                                     usabilitysurvey_type_id=phone_survey_type)
            if existing_survey:
                survey_date_completed = existing_survey[0].date_completed

    passed_vars = {'is_authenticated': is_authenticated, 'consent_submitted': consent_submitted,
                   'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications,
                   'form_errors': form_errors, 'form_values': request.POST, 'survey_date_completed': survey_date_completed}
    passed_vars.update(global_passed_vars)

    if is_wch_study:
        return render_to_response('datacollector/wch/usabilitysurvey_phone.html', passed_vars, context_instance=RequestContext(request))
    return render_to_response('datacollector/usabilitysurvey_phone.html', passed_vars, context_instance=RequestContext(request))

def survey_usability_web(request):
    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    active_notifications = []
    survey_date_completed = False
    form_errors = []
    is_wch_study = False

    # The HTML IDs/names of the questions in the survey template
    questions = {'radio': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9',
                        's1', 's2', 's3', 's4',
                        'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7',
                        'comp_browse', 'comp_frustration', 't2m_use'
                        ],
                 'textarea': ['prev_tests', 'online_vs_inperson', 'complaints', 'future_use'],
                 'checkbox': ['comp_use_communication', 'comp_use_information', 'comp_use_services', 'comp_use_games', 'comp_use_other']
                }
    question_numbers = {'h1': 1, 'h2': 1, 'h3': 1, 'h4': 1, 'h5': 1, 'h6': 1, 'h7': 1, 'h8': 1, 'h9': 1,
                        's1': 2, 's2': 2, 's3': 2, 's4': 2,
                        'e1': 3, 'e2': 3, 'e3': 3, 'e4': 3, 'e5': 3, 'e6': 3, 'e7': 3,
                        'prev_tests': 4,
                        'online_vs_inperson': 5,
                        'complaints': 6,
                        'comp_browse': 7,
                        'comp_frustration': 8,
                        'comp_use_communication': 9,
                        'comp_use_information': 9,
                        'comp_use_services': 9,
                        'comp_use_games': 9,
                        'comp_use_other': 9,
                        't2m_use': 10,
                        'future_use': 11}
    question_order = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9',
                        's1', 's2', 's3', 's4',
                        'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7',
                        'prev_tests',
                        'online_vs_inperson',
                        'complaints',
                        'comp_browse',
                        'comp_frustration',
                        'comp_use_communication',
                        'comp_use_information',
                        'comp_use_services',
                        'comp_use_games',
                        'comp_use_other',
                        't2m_use',
                        'future_use']

    web_survey_type = Subject_UsabilitySurvey_Type.objects.get(name='web').usabilitysurvey_type_id
    if request.user.is_authenticated():
        is_authenticated = True
        date_completed = None
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted

            # Fetch all notifications that are active and have not been dismissed by the user
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = notify.get_active_new(subject)

            # Check for associated bundle
            subject_bundle = Subject_Bundle.objects.filter(subject=subject)
            if subject_bundle:
                if subject_bundle[0].bundle.name_id == 'wch_web' or subject_bundle[0].bundle.name_id == 'wch_phone':
                    is_wch_study = True

            if request.method == "POST":
                # Check for missing responses
                for question_type in questions:
                    question_names = questions[question_type]
                    if question_type == 'checkbox':
                        # Only one checkbox needs to be checked
                        checked_exists = False
                        for n in question_names:
                            if n in request.POST and request.POST[n]:
                                checked_exists = True
                                break
                        if not checked_exists:
                            form_errors += ['You did not provide a response to question #%d' % (question_numbers[n])]
                    else:
                        for n in question_names:
                            if n not in request.POST or not request.POST[n]:
                                form_errors += ['You did not provide a response to question #%d' % (question_numbers[n])]

                # Save the submitted survey responses if there are no errors
                if not form_errors:
                    date_completed = datetime.datetime.now()
                    for question_type in questions:
                        for n in questions[question_type]:
                            if n in request.POST and request.POST[n]:
                                response_id = request.POST[n]
                                question = request.POST['%s_question' % n]
                                key_response = '%s_%s_response' % (n, response_id)
                                if key_response in request.POST:
                                    response = request.POST[key_response]
                                else:
                                    response = response_id
                                Subject_UsabilitySurvey.objects.create(subject=subject,
                                                                       question_id=n,
                                                                       question=question,
                                                                       question_type=question_type,
                                                                       question_order=question_order.index(n),
                                                                       response_id=response_id,
                                                                       response=response,
                                                                       date_completed=date_completed,
                                                                       usabilitysurvey_type_id=web_survey_type)
                    survey_date_completed = date_completed
                else:
                    # Sort the errors and unique only
                    form_errors = sorted(list(set(form_errors)))

            # Check if the survey has been submitted previously
            existing_survey = Subject_UsabilitySurvey.objects.filter(subject=subject,
                                                                     date_completed__isnull=False,
                                                                     usabilitysurvey_type_id=web_survey_type)
            if existing_survey:
                survey_date_completed = existing_survey[0].date_completed

            passed_vars = {'is_authenticated': is_authenticated, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications, 'form_errors': form_errors, 'form_values': request.POST, 'survey_date_completed': survey_date_completed}
            passed_vars.update(global_passed_vars)

            if is_wch_study:
                return render_to_response('datacollector/wch/usabilitysurvey_web.html', passed_vars, context_instance=RequestContext(request))
            return render_to_response('datacollector/usabilitysurvey_web.html', passed_vars, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(website_root)
    else:
        return HttpResponseRedirect(website_root)

def audiorecord(request):

    if request.user.is_authenticated():
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            if request.method == "POST":
                # Get the audio data, save it as a wav file
                # to the server media directory,
                # and return a success message

                msg = "Received " + ", ".join(request.POST.keys())
                files = "Received " + ", ".join(request.FILES.keys())
                instanceid = request.POST['instanceid']
                instance = Session_Task_Instance.objects.filter(session_task_instance_id=instanceid)
                session_response = None
                if instance:
                    instance = instance[0]
                    session_response = Session_Response.objects.filter(session_task_instance=instance)
                    if session_response:
                        session_response = session_response[0]


                for f in request.FILES:
                    # Upload to responses
                    if session_response:
                        file_content = ContentFile(request.FILES[f].read())
                        session_response.value_audio.save('',file_content)

                        # Update the Session Response date of completion
                        Session_Response.objects.filter(session_task_instance=instance).update(date_completed=datetime.datetime.now())

                return_dict = {"status": "success", "msg": msg, "files": files}
                json = simplejson.dumps(return_dict)
                return HttpResponse(json, content_type="application/x-javascript")

    return HttpResponseRedirect(website_root)

def account(request):
    is_authenticated = False
    form_values = {}
    form_errors = []
    save_confirm = False
    save_msg = ""
    json_data = {}
    json_data['status'] = 'fail'
    json_data['email_change'] = 'false'
    active_notifications = []

    # These two flags are passed to the account page so that the base template included therein can use them
    consent_submitted = False
    demographic_submitted = False
    is_email_validated = False
    email_confirm_display = "<div class=\"alert alert-success\"><span class=\"glyphicon glyphicon-ok\"></span> Verified</div>"

    if request.user.is_authenticated():
        is_authenticated = True
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted
            is_email_validated = subject.email_validated

            # Fetch all notifications that are active and have not been dismissed by the user
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = notify.get_active_new(subject)

            if request.method == "GET":
                # A get form request
                if 'resend-email' in request.GET:
                    # Initiate an email validation resend email if the user has provided an email
                    if request.user.email:
                        # Check if there is an existing email token, if not generate one
                        if subject.email_token:
                            email_token = subject.email_token
                        else:
                            email_token = crypto.generate_confirmation_token(request.user.username + request.user.email)
                        confirmation_link = website_hostname + "/activate/" + email_token

                        emailText = "You have updated your email address on " + global_passed_vars['website_name'] + "\n\nPlease click this link to confirm your email address:\n\n<a href=\"" + confirmation_link + "\">" + confirmation_link + "</a>\n\nWhy am I receiving this email? We value your privacy and want to make sure that you are the one who entered this email address in our system. If you received this email by mistake, you can make it all go away by simply ignoring it."

                        emailHtml = """<h2 style="Margin-top: 0;color: #44a8c7;font-weight: 700;font-size: 24px;Margin-bottom: 16px;font-family: Lato,sans-serif;line-height: 32px;text-align: center">You have updated your email address on """ + global_passed_vars['website_name'] + """</h2>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><strong>Please click this link to confirm your email address:</strong></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><u><a href=\"""" + confirmation_link + """\">""" + confirmation_link + """</a></u></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">If the link above does not work, please copy and paste it into your browser's address bar.</p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><strong>Why am I receiving this email?</strong>\r\n We value your privacy and want to make sure that you are the one who entered this email address in our system. If you received this email by mistake, you can make it all go away by simply ignoring it.</p>\r\n"""

                        successFlag = emails.sendEmail(email_username, email_name, [request.user.email], [], [], global_passed_vars['website_name'] + " - Email Confirmation", emailText, emails.emailPre + emailHtml + emails.emailPost)
                        if successFlag:
                            json_data['status'] = 'success'

                            # Update database to keep a record of sent emails, if the mailer was successful
                            Subject_Emails.objects.create(date_sent=datetime.datetime.now().date(), subject=subject, email_from=email_username, email_to=request.user.email, email_type='email_confirmation')
                        else:
                            json_data['error'] = 'The confirmation email could not be sent. Please verify that you have provided a valid email address.'
                    else:
                        json_data['error'] = 'The confirmation email could not be sent. You have not provided an email address.'

                    return HttpResponse(json.dumps(json_data))

            if request.method == "POST":
                form_values = request.POST
                if 'btn-pwdchange' in request.POST:
                    # Perform form validation first
                    # Check that (1) the current password is correct, (2) the new password match,
                    # (3) the new password meets the password field requirements
                    pwd_new = ""
                    if not 'pwd_current' in request.POST or not request.POST['pwd_current']:
                        form_errors += ['You did not provide your current password.']
                    elif not authenticate(username=User.objects.get(id=subject.user_id).username, password=request.POST['pwd_current']):
                        form_errors += ['The current password you provided is incorrect.']

                    if not 'pwd_new1' in request.POST or not 'pwd_new2' in request.POST or \
                        not request.POST['pwd_new1'] or not request.POST['pwd_new2']:
                        form_errors += ['You did not provide your new password (twice).']
                    elif str(request.POST['pwd_new1']) != str(request.POST['pwd_new2']):
                        form_errors += ['The new passwords you provided do not match. You have to repeat the new password twice.']

                    if not form_errors:
                        pwd_new = request.POST['pwd_new1']
                        u = User.objects.get(id=subject.user_id)
                        u.set_password(pwd_new)
                        u.save()
                        save_confirm = True
                        save_msg = "Password updated successfully."
                        json_data['save_msg'] = save_msg
                        json_data['status'] = 'success'
                    else:
                        json_data['error'] = [dict(msg=x) for x in form_errors]

                    return HttpResponse(json.dumps(json_data))

                elif 'btn-save' in request.POST:

                    # Perform form validation first
                    # - check that if any of the email-related options has been selected, the email address is provided
                    user_email = ""
                    if 'email_address' in request.POST:
                        user_email = request.POST['email_address']
                        if user_email:
                            # Validate user email if provided
                            if not regex_email.match(user_email):
                                form_errors += ['The e-mail address you provided does not appear to be valid.']

                    # Dictionary of options which require a user email
                    options_req_email = {'cb_preference_prizes': 'prize draws',
                                         'cb_preference_email_reminders': 'scheduled e-mail reminders',
                                         'cb_preference_email_updates': 'electronic communication regarding study outcomes'}
                    options_selected = set(options_req_email.keys()).intersection(set(request.POST.keys()))
                    if options_selected and not user_email:
                        connector = " || "
                        plur_s = ""
                        if len(options_selected) > 1: plur_s = "s"
                        options_selected_str = connector.join([options_req_email[opt] for opt in options_selected])
                        num_conn = options_selected_str.count(connector)
                        options_selected_str = options_selected_str.replace(connector, ", ", num_conn-1)
                        options_selected_str = options_selected_str.replace(connector, ", and ")

                        form_errors += ['You did not provide an e-mail address. An e-mail address is required since you selected the following option' + plur_s + ': ' + options_selected_str + "."]

                    # - check that an email reminder frequency is specified, if reminders are requested
                    if 'cb_preference_email_reminders' in request.POST and 'radio_email_reminders_freq' not in request.POST:
                        form_errors += ['You have not selected a frequency for the scheduled e-mail reminders.']

                    if not form_errors:

                        current_email = User.objects.filter(id=request.user.id)[0].email
                        if user_email != current_email:
                            json_data['email_change'] = 'true'

                        if user_email:
                            # If the email is different from the existing email for the account, reset the email validated flag, regenerate the email token, and resend a confirmation email
                            if user_email != current_email:
                                new_email_token = crypto.generate_confirmation_token(request.user.username + user_email)
                                Subject.objects.filter(user_id=request.user.id).update(email_validated=0, email_token=new_email_token)

                                confirmation_link = website_hostname + "/activate/" + new_email_token
                                emailText = "You have updated your email address on " + global_passed_vars['website_name'] + "\n\nPlease click this link to confirm your email address:\n\n<a href=\"" + confirmation_link + "\">" + confirmation_link + "</a>\n\nWhy am I receiving this email? We value your privacy and want to make sure that you are the one who entered this email address in our system. If you received this email by mistake, you can make it all go away by simply ignoring it."
                                emailHtml = """<h2 style="Margin-top: 0;color: #44a8c7;font-weight: 700;font-size: 24px;Margin-bottom: 16px;font-family: Lato,sans-serif;line-height: 32px;text-align: center">You have updated your email address on """ + global_passed_vars['website_name'] + """</h2>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><strong>Please click this link to confirm your email address:</strong></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><u><a href=\"""" + confirmation_link + """\">""" + confirmation_link + """</a></u></p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center">If the link above does not work, please copy and paste it into your browser's address bar.</p>\r\n<p style="Margin-top: 0;color: #60666d;font-size: 15px;font-family: sans-serif;line-height: 24px;Margin-bottom: 24px;text-align: center"><strong>Why am I receiving this email?</strong>\r\n We value your privacy and want to make sure that you are the one who entered this email address in our system. If you received this email by mistake, you can make it all go away by simply ignoring it.</p>\r\n"""

                                successFlag = emails.sendEmail(email_username, email_name, [user_email], [], [], global_passed_vars['website_name'] + " - Email Confirmation", emailText, emails.emailPre + emailHtml + emails.emailPost)

                                # Update database to keep a record of sent emails, if the mailer was successful
                                if successFlag:
                                    s = Subject.objects.get(user_id=request.user.id)
                                    Subject_Emails.objects.create(date_sent=datetime.datetime.now().date(), subject=s, email_from=email_username, email_to=user_email, email_type='email_confirmation')

                                # Display "Not verified" msg to user
                                email_confirm_display = "<button type=\"button\" class=\"btn btn-default btn-lg btn-red\" onClick=\"javascript: resendConfirmationEmail(this);\"><span class=\"glyphicon glyphicon-remove\" aria-hidden=\"true\"></span> Not verified. Click to resend confirmation email.</button>"

                            User.objects.filter(id=request.user.id).update(email=user_email)
                        else:
                            User.objects.filter(id=request.user.id).update(email="")

                            # Reset the email validation flag and the email token
                            Subject.objects.filter(user_id=request.user.id).update(email_validated=0, email_token=None)

                            # Hide email verified msg
                            email_confirm_display = ""


                        subject = Subject.objects.get(user_id=request.user.id)
                        today = datetime.datetime.now().date()
                        existing_notif_prizes = Subject_Notifications.objects.filter(Q(date_end__isnull=True) | Q(date_end__gte = today), subject=subject, notification__notification_id="monthlyprize_eligibility")
                        if 'cb_preference_prizes' in request.POST:
                            subject.preference_prizes = 1
                            subject.email_prizes = user_email
                            subject.save()

                            # Trigger notification generation for the user, as they may now be eligible for prizes
                            # (i.e. new notifications to be displayed).
                            if existing_notif_prizes:
                                notify.update_notifications(subject, existing_notif_prizes)
                            else:
                                notify.generate_notifications(subject, "onSessionComplete")

                        else:
                            subject.preference_prizes = 0
                            subject.email_prizes = None
                            subject.save()

                            # The user is no longer eligible for prizes - trigger a notification update (for existing notifications)
                            # if there is an existing monthly prize notification
                            if existing_notif_prizes:
                                notify.update_notifications(subject, existing_notif_prizes)

                        if 'cb_preference_email_reminders' in request.POST:
                            Subject.objects.filter(user_id=request.user.id).update(preference_email_reminders=1, email_reminders=user_email, preference_email_reminders_freq=request.POST['radio_email_reminders_freq'])
                        else:
                            Subject.objects.filter(user_id=request.user.id).update(preference_email_reminders=0, email_reminders=None, preference_email_reminders_freq=None)

                        if 'cb_preference_email_updates' in request.POST:
                            Subject.objects.filter(user_id=request.user.id).update(preference_email_updates=1, email_updates=user_email)
                        else:
                            Subject.objects.filter(user_id=request.user.id).update(preference_email_updates=0, email_updates=None)

                        save_confirm = True
                        save_msg = "Changes saved successfully."
                        json_data['save_msg'] = save_msg
                        json_data['email_confirm_display'] = email_confirm_display
                        json_data['status'] = 'success'
                    else:
                        json_data['error'] = [dict(msg=x) for x in form_errors]

                    return HttpResponse(json.dumps(json_data))

                elif 'btn-withdraw' in request.POST:
                    if 'withdraw_confirm' not in request.POST:
                        form_errors += ['You did not select the confirmation checkbox which acknowledges that you understand the effects of withdrawing from the study.']

                    if not form_errors:
                        # Delete entire user account, including from auth_user
                        Subject.objects.filter(user_id=request.user.id).delete()
                        User.objects.filter(id=request.user.id).delete()
                        auth_logout(request)
                        json_data['status'] = 'success'
                        json_data['website_root'] = '/' + global_passed_vars['website_id']
                    else:
                        json_data['error'] = [dict(msg=x) for x in form_errors]
                    return HttpResponse(json.dumps(json_data))

            else:
                # Fill out the form values with the default values from the database (i.e. mimic the way a POST form works - checkboxes only appear in the collection if they are checked).
                if subject.preference_prizes:
                    form_values['cb_preference_prizes'] = subject.preference_prizes
                if subject.preference_email_reminders:
                    form_values['cb_preference_email_reminders'] = subject.preference_email_reminders
                    form_values['radio_email_reminders_freq'] = subject.preference_email_reminders_freq
                if subject.preference_email_updates:
                    form_values['cb_preference_email_updates'] = subject.preference_email_updates
                form_values['email_address'] = request.user.email

            passed_vars = {'is_authenticated': is_authenticated, 'user': request.user, 'form_values': form_values, 'form_errors': form_errors, 'save_confirm': save_confirm, 'save_msg': save_msg, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications, 'is_email_validated': is_email_validated}
            passed_vars.update(global_passed_vars)

            today = datetime.datetime.now().date()
            subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)
            if subject_bundle:
                subject_bundle = subject_bundle[0]
                if subject_bundle.bundle.name_id == 'uhn_web' or subject_bundle.bundle.name_id == 'uhn_phone':
                    return render_to_response('datacollector/uhn/account.html', passed_vars, context_instance=RequestContext(request))
                elif subject_bundle.bundle.name_id == 'oise':
                    return render_to_response('datacollector/oise/account.html', passed_vars, context_instance=RequestContext(request))
                elif subject_bundle.bundle.name_id == 'wch_web' or subject_bundle.bundle.name_id == 'wch_phone':
                    return render_to_response('datacollector/wch/account.html', passed_vars, context_instance=RequestContext(request))
            return render_to_response('datacollector/account.html', passed_vars, context_instance=RequestContext(request))
        else:
            # If user is authenticated with as a User that doesn't exist as a Subject (i.e. for this study), then go to main page
            return HttpResponseRedirect(website_root)
    else:
        # If user is not authenticated, just go to main page
        return HttpResponseRedirect(website_root)


def about(request):
    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    active_notifications = []
    is_uhn_study = False

    if request.user.is_authenticated():
        is_authenticated = True
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted

            # Fetch all notifications that are active and have not been dismissed by the user
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = notify.get_active_new(subject)

            # Check if UHN user
            today = datetime.datetime.now().date()
            subject_bundle = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today)

            # TODO: Create about.html page for UHN study and re-factor this section
            if subject_bundle:
                subject_bundle = subject_bundle[0]
                if subject_bundle.bundle.name_id == 'uhn_web' or subject_bundle.bundle.name_id == 'uhn_phone':
                    is_uhn_study = True

    passed_vars = {
        'is_authenticated': is_authenticated, 'user': request.user,
        'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted,
        'active_notifications': active_notifications, 'is_uhn_study': is_uhn_study
    }
    passed_vars.update(global_passed_vars)

    return render_to_response('datacollector/about.html', passed_vars, context_instance=RequestContext(request))

def error(request, error_id):
    is_authenticated = False
    consent_submitted = False
    demographic_submitted = False
    active_notifications = []

    if request.user.is_authenticated():
        is_authenticated = True
        subject = Subject.objects.filter(user_id=request.user.id)
        if subject:
            subject = subject[0]
            consent_submitted = subject.date_consent_submitted
            demographic_submitted = subject.date_demographics_submitted

            # Fetch all notifications that are active and have not been dismissed by the user
            # (NB: Q objects must appear before keyword parameters in the filter)
            active_notifications = notify.get_active_new(subject)

    passed_vars = {'error_id': error_id, 'is_authenticated': is_authenticated, 'user': request.user, 'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted, 'active_notifications': active_notifications}
    passed_vars.update(global_passed_vars)

    return render_to_response('datacollector/error.html', passed_vars, context_instance=RequestContext(request))


def pagetime(request):

    if request.method == "POST":

        session_task_id = request.POST['sessiontaskid']
        time_elapsed = request.POST['timeelapsed']

        # Save to db
        current_task = Session_Task.objects.filter(session_task_id=session_task_id)
        if current_task:
            current_time_elapsed = current_task[0].total_time
            current_task.update(total_time=int(current_time_elapsed) + int(time_elapsed))

        return_dict = {"status": "success"}
        json = simplejson.dumps(return_dict)
        return HttpResponse(json, content_type="application/x-javascript")
    return HttpResponseRedirect(website_root)


@csrf_exempt
def bundle_completion_validate(request):
    # Takes: POST request with parameters "username" and "confirmation_token"
    # Returns: JSON with parameters "status" ("success"/"fail"), "valid" ("yes"/"no")
    json_data = {"status": "success"}
    is_valid = False
    today = datetime.datetime.now().date()

    if request.method == "POST":
        if "username" in request.POST and "completion_token" in request.POST:
            username = request.POST["username"]
            completion_token = request.POST["completion_token"]
            if username and completion_token and len(completion_token) == 128 and completion_token.isalnum():

                # Check user exists
                u = User.objects.filter(username=username)
                if u:
                    u = u[0]
                    # Check associated subject exists
                    s = Subject.objects.filter(user_id=u.id)
                    if s:
                        s = s[0]
                        # Check if token exists in database for a Subject_Bundle pair for the same subject, and that it hasn't been used before
                        sb = Subject_Bundle.objects.filter(Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), active_startdate__lte=today, completion_token=completion_token, subject=s, completion_token_usedate__isnull=True)
                        if sb:
                            sb = sb[0]
                            # Check if the subject has completed all required sessions
                            completed_sessions = Session.objects.filter(subject=s, end_date__isnull=False, start_date__gte=sb.active_startdate)
                            if completed_sessions and (not sb.completion_req_sessions or len(completed_sessions) >= sb.completion_req_sessions):
                                is_valid = True

        if is_valid:
            json_data["valid"] = "yes"
        else:
            json_data["valid"] = "no"
        json = simplejson.dumps(json_data)

        response = HttpResponse(json)
        response["Content-type"] = "application/json"
        response["Access-Control-Allow-Origin"] = "*" # https://tasks.crowdflower.com
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Accept, Content-Type, X-CSRFToken, X-Requested-With"
        return response
    return HttpResponse("Unauthorized", status=401)
