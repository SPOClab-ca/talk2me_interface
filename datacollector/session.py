import datetime
import random

from csc2518.settings import STATIC_URL, SUBSITE_ID, UHN_STUDY, OISE_STUDY, WCH_STUDY
from django.http import HttpResponseRedirect
from django.db.models import Q, Sum
from datacollector.models import Bundle, Bundle_Task_Field_Value, Session, Session_Response, Session_Task, Session_Task_Instance, Session_Task_Instance_Value,Session_Type, Subject, Subject_Bundle, Task, Task_Field, Task_Field_Value

website_root = '/'
if SUBSITE_ID: website_root += SUBSITE_ID
UHN_WEBSITE_ROOT = website_root + UHN_STUDY
OISE_WEBSITE_ROOT = website_root + OISE_STUDY
WCH_WEBSITE_ROOT = website_root + WCH_STUDY


# Bundles
WCH_WEB_BUNDLE = Bundle.objects.get(name_id='wch_web')
WCH_PHONE_BUNDLE = Bundle.objects.get(name_id='wch_phone')

# Session_Type
SESSION_TYPE_WEB = Session_Type.objects.get(name='website')
SESSION_TYPE_PHONE = Session_Type.objects.get(name='phone')

def startsession(request, session_type):
    if request.user.is_authenticated():
        subject = Subject.objects.get(user_id=request.user.id)
        subject_bundles = Subject_Bundle.objects.filter(subject=subject)

        is_wch_bundle = False
        for subject_bundle in subject_bundles:
            if subject_bundle.bundle.bundle_id == WCH_WEB_BUNDLE.bundle_id or subject_bundle.bundle.bundle_id == WCH_PHONE_BUNDLE.bundle_id:
                is_wch_bundle = True
                break

        if is_wch_bundle:
            new_session = generate_session_wch(subject, session_type)
            return HttpResponseRedirect(WCH_WEBSITE_ROOT + "session/" + str(new_session.session_id))
        else:
            return HttpResponseRedirect(website_root + "500")
    else:
        return HttpResponseRedirect(website_root)

def startsession_web(request):
    return startsession(request, SESSION_TYPE_WEB)

def startsession_phone(request):
    return startsession(request, SESSION_TYPE_PHONE)

def generate_session_wch(subject, session_type):
    '''
        Generate session for WCH
    '''
    # Get previous 6 sessions, if applicable
    prev_sessions = Session.objects.filter(subject=subject).order_by('-start_date')
    if len(prev_sessions) >= 6:
        prev_sessions = prev_sessions[:6]

    prev_session_ids = [prev_session.session_id for prev_session in prev_sessions]

    # Get active task bundles
    # The active date range for the bundle is inclusive.
    today = datetime.datetime.now().date()
    active_bundles = Subject_Bundle.objects.filter( Q(active_enddate__isnull=True) | Q(active_enddate__gte=today), subject=subject, active_startdate__lte=today )
    active_tasks = []
    active_tasks_num_instances = {}
    active_bundle_tasks = {}

    if not active_bundles:
        return

    for subj_bundle in active_bundles:
        bundle_id = subj_bundle.bundle.name_id
        bundle_tasks = subj_bundle.bundle.bundle_task_set.all()

        # For each Bundle_Task record the task and the num instances
        for x in bundle_tasks:
            active_tasks += [x.task]
            active_tasks_num_instances[x.task.task_id] = x.default_num_instances
            active_bundle_tasks[x.task.task_id] = x
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
            # Sum up the instances for each display field for the task (i.e., for the GDS task)
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

        for field in task_fields_display:

            # If the field doesn't have a specified number of instances, then use the task-level number of instances.
            field_num_instances = field.default_num_instances
            if not field_num_instances:
                field_num_instances = num_instances
            ## TODO: Only query for AT MOST previous 6 sessions. otherwise, "restart" count
            existing_instances = Session_Task_Instance_Value.objects.filter(task_field=field, session_task_instance__session_task__session__subject=subject, session_task_instance__session_task__session__session_id__in=prev_session_ids)
            existing_values = [v.value for v in existing_instances]

            selected_values = []

            # If there are specified task field values in the bundle task, select those.
            specified_values = []
            specified_values_from_db = []
            if bundle_task is not None:
                specified_values_from_db = Bundle_Task_Field_Value.objects.filter(bundle_task_id=bundle_task.bundle_task_id).order_by('bundle_task_field_value_id')
            if len(specified_values_from_db) > 0:
                specified_values = specified_values_from_db
                selected_values = [x.task_field_value for x in specified_values[len(existing_instances):len(existing_instances)+field_num_instances]]
            else:
                # Otherwise, select values IN ORDER that haven't been viewed yet.

                # Add to selected values. Make sure not to add field values that are associated with each other, or are already selected, or have been seen by the subject before in previous sessions. NB: here we are assuming that the total number of values for each field in the db is at least as big as the default number of instances for the field.
                limits = []
                while len(selected_values) < field_num_instances:

                    field_values = Task_Field_Value.objects.filter(task_field=field,*limits).exclude(value__in=existing_values)
                    # Select the next possible field value
                    if field_values:
                        selected_values += [field_values[0]]
                    else:
                        # If there aren't any results, relax the query by restricting only to values that haven't been seen before
                        field_values = Task_Field_Value.objects.filter(task_field=field).exclude(value__in=existing_values)
                        if field_values:
                            selected_values += [field_values[0]]
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
