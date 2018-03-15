import re
import copy
import datetime
import json

from csc2518.settings import STATIC_URL
from datacollector.models import Field_Type, Session, Session_Response, Session_Task, Session_Task_Instance, \
                                 Session_Task_Instance_Value, Task, Task_Field, Task_Field_Data_Attribute

from constants import READING_FLUENCY_TASK_ID

WORD_COMPLETION = 'word_completion_oise'
PICTURE_DESCRIPTION = 'picture_description_oise'
STORY_RETELLING = 'story_retelling_oise'
WORD_MAP = 'word_map_oise'
PUZZLE_SOLVING = 'puzzle_solving_oise'

FIELD_TYPE_INPUT_ID = Field_Type.objects.get(name='input')
FIELD_TYPE_DISPLAY_ID = Field_Type.objects.get(name='display')

def display_session_task_instance(session_task_id):
    """
    Update variables for displaying session task instance
        :param session_task_id:
    """

    is_last_task_instance = False


    # Retrieve active task instance values
    task_id = Session_Task.objects.get(session_task_id=session_task_id) \
              .task_id
    task_name = Task.objects.get(task_id=task_id).name_id
    session_task_instances = Session_Task_Instance.objects.filter \
                             (session_task_id=session_task_id)
    session_task_instance_ids = [session_task_instance.session_task_instance_id for \
                                 session_task_instance in session_task_instances]
    # session_response_objects = [Session_Response.objects.get(session_task_instance=session_task_instance, \
    #                             date_completed__isnull=True) for session_task_instance in session_task_instances]
    session_response_objects = Session_Response.objects \
                               .filter(session_task_instance_id__in=session_task_instance_ids, date_completed__isnull=True)

    if session_response_objects:
        active_session_task_instance = session_response_objects[0]


        # Only display one Session_Response object at a time
        if task_name == 'reading_fluency':
            display_field, response_field, requires_audio = display_reading_fluency(active_session_task_instance.session_task_instance_id)
        elif task_name == 'picture_description_oise':
            display_field, response_field, requires_audio = display_picture_description(active_session_task_instance.session_task_instance_id)
        elif task_name == 'story_retelling_oise':
            display_field, response_field, requires_audio = display_story_retelling(active_session_task_instance.session_task_instance_id)
        elif task_name == WORD_COMPLETION:
            # For word completion, display all session_task_instances on the same page
            display_field, response_field, requires_audio = display_word_completion(session_task_id)
        elif task_name == WORD_MAP:
            display_field, response_field, requires_audio = display_word_map(active_session_task_instance.session_task_instance_id)
        elif task_name == PUZZLE_SOLVING:
            display_field, response_field, requires_audio = display_puzzle_solving(active_session_task_instance.session_task_instance_id)

        if len(session_response_objects) == 1:
            is_last_task_instance = True

        return active_session_task_instance, display_field, response_field, requires_audio, is_last_task_instance
    #else:
        # TODO: All tasks were complete???

def submit_response(request):
    print('submit response')
    json_data = {}
    # Validate the form first
    # Determine the order of the questions associated with this task (e.g., non-select questions have 'response' fields, whereas
    # select questions have 'response_{instanceid}' fields).
    # active_task_questions = Session_Task_Instance_Value.objects.filter(session_task_instance__session_task=active_task, task_field__field_type__name='display')
    form_responses = request.POST.getlist('response')
    form_instances = request.POST.getlist('instanceid')
    responses = copy.deepcopy(form_responses)
    instances = copy.deepcopy(form_instances)
    print(responses)
    print(instances)
    if len(form_instances) > 1:
        active_task_instance_questions = Session_Task_Instance_Value.objects \
                                         .filter(session_task_instance_id__in=form_instances)
    else:
        instance_id = request.POST['instanceid']
        active_task_instance_questions = Session_Task_Instance_Value.objects \
                                        .filter(session_task_instance_id=instance_id)
    if active_task_instance_questions:
        active_task_instance_question = active_task_instance_questions[0]
    question_field = Task_Field.objects \
                     .get(task_field_id=active_task_instance_question.task_field_id)
    response_field = Task_Field.objects.get(assoc_id=question_field.task_field_id)
    form_errors = []
    counter_question = 0
    # If audio, the Session_Response object will already be updated
    # Need to check if the Session_Task is completed
    associated_task_instances = Session_Task_Instance.objects \
                                   .filter(session_task=active_task_instance_question \
                                                        .session_task_instance \
                                                        .session_task)
    for next_instance in instances:
        if response_field.field_data_type.name == 'select':
            audio_label = 'response_audio_' + str(next_instance)
            if not audio_label in request.POST:
                response_label = 'response_' + str(next_instance)
                if response_label in request.POST:
                    next_response = request.POST[response_label]
                    if not next_response:
                        form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
                    if not next_instance:
                        form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
                    instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)
                    Session_Response.objects.filter(session_task_instance=instance).update(value_text=next_response,date_completed=datetime.datetime.now())
                    if not instance:
                        form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
                else:
                    form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
        elif response_field.field_data_type.name == 'text':
            response_text = responses[counter_question]
            if response_text.strip():
                instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)
                if instance:
                    Session_Response.objects.filter(session_task_instance=instance) \
                                    .update(value_text=response_text,\
                                            date_completed=datetime.datetime.now())
                else:
                    form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
            else:
                form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
        elif response_field.field_data_type.name == 'word_map':
            response_text = 'dummy answer'
            if response_text.strip():
                instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)
                if instance:
                    Session_Response.objects.filter(session_task_instance=instance) \
                                    .update(value_text=response_text,\
                                            date_completed=datetime.datetime.now())
                else:
                    form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
            else:
                form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
        counter_question += 1


        incomplete_session_responses = Session_Response.objects \
                                      .filter(session_task_instance__in=associated_task_instances,
                                              date_completed__isnull=True)

        # Display the next task instance
        if incomplete_session_responses:
            session_task_in_progress = True

        # Update Session_Task
        else:
            print('Update session task')
            active_task = active_task_instance_question.session_task_instance.session_task
            print(Session_Task.objects.filter(session=active_task.session,task=active_task.task))
            Session_Task.objects.filter(session=active_task.session,task=active_task.task).update(date_completed=datetime.datetime.now())
            session_task_in_progress = False

            # Update Session if necessary
            session_tasks = Session_Task.objects.filter(session=active_task.session, date_completed__isnull=True)
            if not session_tasks:
                print('update session')
                Session.objects.filter(session_id=active_task.session.session_id).update(end_date=datetime.datetime.now())
 
    # if response_field.field_data_type.name == 'select' or response_field.field_data_type.name == 'audio':
    #     # If the associated response field is 'select' or 'audio', then there will be 'response_{instanceid}' fields
    #     audio_label = 'response_audio_' + str(next_instance)
    #     if not audio_label in request.POST:
    #         response_label = 'response_' + str(next_instance)
    #         if response_label in request.POST:
    #             next_response = request.POST[response_label]
    #                 if not next_response:
    #                     form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
    #                 if not next_instance:
    #                     form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
    #                 else:
    #                     instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)
    #                     if not instance:
    #                         form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
    #             else:
    #                 form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
    #     else:
    #         # Otherwise, look for 'response' fields
    #         next_response = responses.pop(0)
    #         if not next_response:
    #             form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
    #         if not next_instance:
    #             form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
    #         else:
    #             instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)
    #             if not instance:
    #                 form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
    #     counter_question += 1


    # # Process any input, textarea (text), and multiselect responses
    # if not form_errors:
    #     responses = copy.deepcopy(form_responses)
    #     instances = copy.deepcopy(form_instances)

    #     for question in active_task_questions:
    #         question_response = Task_Field.objects.get(assoc=question.task_field)

    #         next_instance = instances.pop(0)
    #         if question_response.field_data_type.name == 'select' or question_response.field_data_type.name == 'audio' or (active_task.task_id == RIG_TASK_ID and is_uhn_study):
    #             # If the associated response field is 'select' or 'audio', then there will be 'response_{instanceid}' fields
    #             audio_label = 'response_audio_' + str(next_instance)
    #             if not audio_label in request.POST:
    #                 response_label = 'response_' + str(next_instance)
    #                 if response_label in request.POST:
    #                     next_response = request.POST[response_label]
    #                     instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)[0]

    #                     # Find the response field type for this task
    #                     response_data_type = Task_Field.objects.filter(task=instance.session_task.task,field_type__name='input')[0].field_data_type

    #                     if response_data_type == 'select':
    #                         Session_Response.objects.filter(session_task_instance=instance).update(value_text=next_response,date_completed=datetime.datetime.now())
    #                     else:
    #                         Session_Response.objects.filter(session_task_instance=instance).update(value_text=next_response,date_completed=datetime.datetime.now())
    #         else:
    #             # Otherwise, look for 'response' fields
    #             next_response = responses.pop(0)
    #             instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)[0]

    #             # Find the response field type for this task
    #             response_data_type = Task_Field.objects.filter(task=instance.session_task.task,field_type__name='input')[0].field_data_type

    #             # Update the appropriate entry in the database (NB: 'audio' responses are not handled here; they are saved to database as soon as they are recorded, to avoid loss of data)
    #             if response_data_type == 'multiselect':
    #                 Session_Response.objects.filter(session_task_instance=instance).update(value_multiselect=next_response,date_completed=datetime.datetime.now())
    #             else:
    #                 Session_Response.objects.filter(session_task_instance=instance).update(value_text=next_response,date_completed=datetime.datetime.now())


    #     # Mark the task as submitted
    #     Session_Task.objects.filter(session=session,task=active_task.task).update(date_completed=datetime.datetime.now())

    json_data['status'] = 'success'

## SUBMITTING ANSWERS
    if form_errors:
        json_data['error'] = [dict(msg=x) for x in form_errors]

    return json_data

def display_reading_fluency(session_task_instance_id):
    task_id = Task.objects.get(name_id='reading_fluency')
    task_instances = Session_Task_Instance_Value.objects \
                    .filter(session_task_instance_id=session_task_instance_id)

    print(session_task_instance_id)
    print(task_instances)

    task_field_question = Task_Field.objects.get(name='reading_fluency_question')
    task_field_story = Task_Field.objects.get(name='reading_fluency_story')
    # For stories, we only display one question field and one response field
    task_instance = task_instances[0]
    task_field_id = task_instance.task_field_id

    if task_field_id == task_field_story.task_field_id:

        response = Task_Field.objects.get(assoc_id=task_field_id)
        response_field, requires_audio  = display_response(task_instance, str(response.field_data_type))
        print('Response field: ' + response_field)

    # For multiple choice questions, we display one question field and multiple response fields
    elif task_field_id == task_field_question.task_field_id:
        response = Task_Field.objects.get(assoc_id=task_field_id)
        response_instances = Session_Task_Instance_Value.objects \
                                .filter(session_task_instance_id=session_task_instance_id, \
                                 task_field_id=response.task_field_id)
        print(response_instances)
        response_field = ''
        for response_instance in response_instances:
            response_instance_field, _ = display_response(response_instance, \
                                                          str(response.field_data_type))
            print(response_instance_field)
            print(response.field_data_type)
        response_field += response_instance_field

        requires_audio = False

    question = Task_Field.objects.get(task_field_id=task_field_id)
    display_field = display_question(task_instance, str(question.field_data_type))
    print('Display field: ' + display_field)

    return display_field, response_field, requires_audio

def display_picture_description(session_task_instance_id):
    task_id = Task.objects.get(name_id='picture_description_oise').task_id
    task_instance = Session_Task_Instance_Value.objects \
                    .get(session_task_instance_id=session_task_instance_id)
    question = Task_Field.objects.get(task_id=task_id, field_type_id=1)
    response = Task_Field.objects.get(task_id=task_id, field_type_id=2)

    print(question.field_data_type)
    display_field = display_question(task_instance, str(question.field_data_type))
    print('Display field: ' + display_field)

    response_field, requires_audio  = display_response(task_instance, str(response.field_data_type))
    print('Response field: ' + response_field)

    return display_field, response_field, requires_audio

def display_story_retelling(session_task_instance_id):
    task_id = Task.objects.get(name_id='story_retelling_oise').task_id
    task_instance = Session_Task_Instance_Value.objects \
                    .get(session_task_instance_id=session_task_instance_id)

    task_field_id = task_instance.task_field_id
    story_field = Task_Field.objects.get(task_field_id=task_field_id)

    response = Task_Field.objects.get(assoc_id=task_field_id, field_data_type=2)

    print(story_field.field_data_type)
    display_field = display_question(task_instance, str(story_field.field_data_type))
    print('Display field: ' + display_field)

    response_field, requires_audio  = display_response(task_instance, str(response.field_data_type))
    print('Response field: ' + response_field)

    return display_field, response_field, requires_audio

def display_word_completion(session_task_id):
    task_id = Task.objects.get(name_id=WORD_COMPLETION).task_id
    task_instances = Session_Task_Instance.objects \
                    .filter(session_task_id=session_task_id)
    question = Task_Field.objects.get(task_id=task_id, \
                                      field_type_id=FIELD_TYPE_DISPLAY_ID)
    response = Task_Field.objects.get(task_id=task_id, \
                                      field_type_id=FIELD_TYPE_INPUT_ID)

    print(question.field_data_type)
    display_field = ''
    for idx, task_instance in enumerate(task_instances):
        task_instance_value = Session_Task_Instance_Value.objects \
                              .get(session_task_instance_id=task_instance \
                                                            .session_task_instance_id)
        display_field += ('%d. ' % (idx + 1)) + display_question(task_instance_value, str(question.field_data_type)) + '<br>'
    print('Display field: ' + display_field)

    print(response.field_data_type)
    response_field, requires_audio  = display_response(task_instance_value, str(response.field_data_type))
    print('Response field: ' + response_field)

    return '<br>', display_field, False

def display_word_map(session_task_instance_id):
    task_id = Task.objects.get(name_id=WORD_MAP).task_id
    task_instance = Session_Task_Instance_Value.objects \
                    .get(session_task_instance_id=session_task_instance_id)
    question = Task_Field.objects.get(task_id=task_id, field_type_id=FIELD_TYPE_DISPLAY_ID)

    print(question.field_data_type)
    display_field = '<h2>'
    display_field += display_question(task_instance, str(question.field_data_type))
    display_field += '</h2>'
    print('Display field: ' + display_field)

    ## TODO: Response field

    return '', display_field, False

def display_puzzle_solving(session_task_instance_id):
    task_id = Task.objects.get(name_id=PUZZLE_SOLVING).task_id
    print(session_task_instance_id)

    image_field = Task_Field.objects.get(task_id=task_id, \
                                         field_type_id=FIELD_TYPE_DISPLAY_ID)
    response = Task_Field.objects.get(assoc_id=image_field.task_field_id, \
                                      field_type_id=FIELD_TYPE_INPUT_ID)

    task_instance = Session_Task_Instance_Value.objects \
                    .get(session_task_instance_id=session_task_instance_id, \
                         task_field_id=image_field.task_field_id)
    print(image_field.field_data_type)
    display_field = display_question(task_instance, str(image_field.field_data_type))
    print('Display field: ' + display_field)

    response_field = ''
    response_field_instances = Session_Task_Instance_Value.objects \
                               .filter(session_task_instance_id=session_task_instance_id, \
                                task_field_id=response.task_field_id)
    for response_field_task_instance in response_field_instances:
        response_field_instance, _  = display_response(response_field_task_instance, \
                                                       str(response.field_data_type))
    response_field += response_field_instance
    #print('Response field: ' + response_field)

    return display_field, response_field, False

def display_question(instance_value, field_data_type):
    # Determine how to display the value based on the field type
    display_field = ""

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
        display_field = "<img class=\"oise-picture-description\" src='" + STATIC_URL + "img/" + instance_value.value + "' style=\"" + style_attributes + "\" />"
    elif field_data_type == "text_withblanks":
        display_field = (instance_value.value).replace("[BLANK]", "<input class='form-field' name='response' type='text' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />")
    elif field_data_type == "text_newlines":
        sents = instance_value.value.split(" || ")
        regex_nonalpha = re.compile(r"^[^a-zA-Z0-9]+$")
        display_field = "<br>".join([sent[0].lower() + sent[1:] for sent in sents if not regex_nonalpha.findall(sent)])
    elif field_data_type == "text_read_aloud":
        display_field = instance_value.value.replace('\n', '<br>')
        display_field += '[TO BE READ ALOUD]'
        print(display_field)
    elif field_data_type == "word_map":
        display_field = '<h2>' + instance_value.value + '</h2>'
        display_field += "<input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
    elif field_data_type == "audio":
        display_field = '<audio controls>'
        display_field += '<source src="%saudio/oise/%s" type="audio/mpeg">' \
                            % (STATIC_URL, instance_value.value)
        display_field += 'Your browser does not support the audio element.</audio>'
    else:
        display_field = instance_value.value.replace('\n', '<br>')

    return display_field

def display_response(instance_value, field_data_type):
    requires_audio = False
    response_field = ""
    response_object = Session_Response.objects.filter(session_task_instance=instance_value.session_task_instance)[0]
    instance_id = str(instance_value.session_task_instance_id)
    # Construct style attributes string from the specified field data attributes
    field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=instance_value.task_field)
    style_attributes = ";".join([str(attr.name) + ": " + str(attr.value) for attr in field_data_attributes])

    if field_data_type == "audio":
        requires_audio = True

        # If the display field is to be kept visible during the audio the subject provides, keep it visible and directly show a recording button
        keep_visible = instance_value.task_field.keep_visible
        print(not keep_visible)
        response_field = ""
        if not keep_visible:
            response_field += "<p><input class='btn btn-primary btn-med btn-fixedwidth' type='button' onClick='javascript: hideDisplayOise(this);' value='Continue'></p>"
        response_field += "<p id='record-btn_" + instance_id + "'"
        if not keep_visible:
            response_field += " class='invisible'"
        response_field += "><input id='btn_recording_" + instance_id + "' type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: toggleRecording(this);' value='Start recording'>&nbsp;" + "<span class='invisible' id='status_recording_" + instance_id + "'><img src='" + STATIC_URL + "img/ajax_loader.gif' /> <span id='status_recording_" + instance_id + "_msg'></span></span><input class='form-field' type='hidden' id='response_audio_" + instance_id + "' name='response_audio_" + instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' /></p>"

    elif field_data_type == "select":
        existing_value = ""
        if response_object.value_text:
            existing_value = response_object.value_text
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
    
    # regex for field data type 'scale' (scale_{from}_{to})
    #regex_scale = re.compile(r'scale\_([0-9]+)\_([0-9]+)')
    '''
    elif field_data_type == "text":
        existing_value = ""
        if response_object.value_text:
            existing_value = response_object.value_text
        response_field = "<input class='form-field form-control' name='response' type='text' value='" + existing_value + "' style=\"" + style_attributes + "\"><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
    elif field_data_type == "multiselect":
        existing_value = ""
        if response_object.value_text:
            existing_value = response_object.value_text
        response_field = "<input class='form-field form-control' name='response' type='text' value='" + existing_value + "'><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
   
    
    elif field_data_type == "textarea":
        existing_value = ""
        if response_object.value_text:
            existing_value = response_object.value_text
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

        print(response_field)
    

    # elif regex_scale.findall(field_data_type):
    #     matches = regex_scale.findall(field_data_type)
    #     scale_start = matches[0][0]
    #     scale_end = matches[0][1]

    #     response_field = "<div class='row'><div class='col-xs-6'><div class='scale_" + str(scale_start) + "_" + str(scale_end) + "' style=\"" + style_attributes + "\"></div><div class='scale_display' style='font-size: 20px;'></div><input class='form-field' name='response' type='hidden' value='' /></div></div><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
    '''
    return response_field, requires_audio
# SUBMIT


                        # Validate the form first
                        # Determine the order of the questions associated with this task (e.g., non-select questions have 'response' fields, whereas
                        # select questions have 'response_{instanceid}' fields).
                        # active_task_questions = Session_Task_Instance_Value.objects.filter(session_task_instance__session_task=active_task, task_field__field_type__name='display')
                        # form_responses = request.POST.getlist('response')
                        # form_instances = request.POST.getlist('instanceid')
                        # responses = copy.deepcopy(form_responses)
                        # instances = copy.deepcopy(form_instances)
                        # counter_question = 0
                        # for question in active_task_questions:
                        #     question_response = Task_Field.objects.get(assoc=question.task_field)

                        #     next_instance = instances.pop(0)
                        #     if question_response.field_data_type.name == 'select' or question_response.field_data_type.name == 'audio' or (active_task.task_id == RIG_TASK_ID and is_uhn_study):
                        #         # If the associated response field is 'select' or 'audio', then there will be 'response_{instanceid}' fields
                        #         audio_label = 'response_audio_' + str(next_instance)
                        #         if not audio_label in request.POST:
                        #             response_label = 'response_' + str(next_instance)
                        #             if response_label in request.POST:
                        #                 next_response = request.POST[response_label]
                        #                 if not next_response:
                        #                     form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
                        #                 if not next_instance:
                        #                     form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
                        #                 else:
                        #                     instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)
                        #                     if not instance:
                        #                         form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
                        #             else:
                        #                 form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
                        #     else:
                        #         # Otherwise, look for 'response' fields
                        #         next_response = responses.pop(0)
                        #         if not next_response:
                        #             form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
                        #         if not next_instance:
                        #             form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
                        #         else:
                        #             instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)
                        #             if not instance:
                        #                 form_errors += ['Question #' + str(counter_question+1) + ' is invalid.']
                        #     counter_question += 1


                        # # Process any input, textarea (text), and multiselect responses
                        # if not form_errors:
                        #     responses = copy.deepcopy(form_responses)
                        #     instances = copy.deepcopy(form_instances)

                        #     for question in active_task_questions:
                        #         question_response = Task_Field.objects.get(assoc=question.task_field)

                        #         next_instance = instances.pop(0)
                        #         if question_response.field_data_type.name == 'select' or question_response.field_data_type.name == 'audio' or (active_task.task_id == RIG_TASK_ID and is_uhn_study):
                        #             # If the associated response field is 'select' or 'audio', then there will be 'response_{instanceid}' fields
                        #             audio_label = 'response_audio_' + str(next_instance)
                        #             if not audio_label in request.POST:
                        #                 response_label = 'response_' + str(next_instance)
                        #                 if response_label in request.POST:
                        #                     next_response = request.POST[response_label]
                        #                     instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)[0]

                        #                     # Find the response field type for this task
                        #                     response_data_type = Task_Field.objects.filter(task=instance.session_task.task,field_type__name='input')[0].field_data_type

                        #                     if response_data_type == 'select':
                        #                         Session_Response.objects.filter(session_task_instance=instance).update(value_text=next_response,date_completed=datetime.datetime.now())
                        #                     else:
                        #                         Session_Response.objects.filter(session_task_instance=instance).update(value_text=next_response,date_completed=datetime.datetime.now())
                        #         else:
                        #             # Otherwise, look for 'response' fields
                        #             next_response = responses.pop(0)
                        #             instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)[0]

                        #             # Find the response field type for this task
                        #             response_data_type = Task_Field.objects.filter(task=instance.session_task.task,field_type__name='input')[0].field_data_type

                        #             # Update the appropriate entry in the database (NB: 'audio' responses are not handled here; they are saved to database as soon as they are recorded, to avoid loss of data)
                        #             if response_data_type == 'multiselect':
                        #                 Session_Response.objects.filter(session_task_instance=instance).update(value_multiselect=next_response,date_completed=datetime.datetime.now())
                        #             else:
                        #                 Session_Response.objects.filter(session_task_instance=instance).update(value_text=next_response,date_completed=datetime.datetime.now())


                        #     # Mark the task as submitted
                        #     Session_Task.objects.filter(session=session,task=active_task.task).update(date_completed=datetime.datetime.now())

                        #    json_data['status'] = 'success'

                    ## SUBMITTING ANSWERS
                    # if form_errors:
                    #     json_data['error'] = [dict(msg=x) for x in form_errors]
                    # return HttpResponse(json.dumps(json_data))


# DISPLAY
             # active_task = Session_Task.objects.filter(session=session,date_completed__isnull=True).order_by('order')
            #     if not active_task:
            #         # All tasks in the current session have been completed - mark the session as complete with an end date stamp, and display acknowledgement. Display summary. Trigger notification generation.
            #         display_thankyou = True

            #         completed_date = datetime.datetime.now()
            #         Session.objects.filter(session_id=session.session_id).update(end_date=completed_date)

            #         summary_tasks = Session_Task.objects.filter(session=session).order_by('order')
            #         counter = 1
            #         for next_task in summary_tasks:
            #             next_task_instances = Session_Task_Instance.objects.filter(session_task=next_task).aggregate(count_instances=Count('session_task_instance_id'))
            #             session_summary += "<tr><td>" + str(counter) + "</td><td>" + next_task.task.name + "</td><td>" + str(next_task_instances['count_instances']) + "</td></tr>"
            #             counter += 1

            #         # Trigger notifications that are linked to session completion
            #         notify.generate_notifications(subject, "onSessionComplete")

            #     else:
            

            #         # Add an attribute for each task, defining it as serial or not
            #         if active_task.name_id == "stroop":
            #             serial_instances = True
            #             first_instance_id = str(active_task_instance_values[0].session_task_instance.session_task_instance_id)
            #             serial_startslide = "<div class='space-bottom-med space-top-med stroop-slide'><div style='font-size: 72px;'>&nbsp;</div><button type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: stroopTaskBegin(this);'>Start</button><input class='form-field' type='hidden' id='response_audio_" + first_instance_id + "' name='response_audio_" + first_instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + first_instance_id + "' /></div>"
            #             requires_audio = True

            #         count_inst = 0
            #         for instance_value in active_task_instance_values:

            #             # Determine how to display the value based on the field type
            #             display_field = ""
            #             response_field = ""
            #             field_data_type = instance_value.task_field.field_data_type.name

            #             # Construct style attributes string from the specified field data attributes
            #             field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=instance_value.task_field)
            #             style_attributes = ";".join([str(attr.name) + ": " + str(attr.value) for attr in field_data_attributes])

            #             session_task_instance = instance_value.session_task_instance
            #             instance_id = str(instance_value.session_task_instance.session_task_instance_id)

            #             if field_data_type == "text":
            #                 display_field = instance_value.value.replace('\n', '<br>')
            #             elif field_data_type == "text_well":
            #                 display_field = "<div class='well well-lg space-bottom-small'>" + instance_value.value.replace('\n', '<br>') + "</div>"
            #             elif field_data_type == "image":
            #                 display_field = "<img src='" + STATIC_URL + "img/" + instance_value.value + "' style=\"" + style_attributes + "\" />"
            #             elif field_data_type == "text_withblanks":
            #                 display_field = (instance_value.value).replace("[BLANK]", "<input class='form-field' name='response' type='text' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />")
            #             elif field_data_type == "timer_rig":

            #                 # Parse out the duration of the timer
            #                 timer_duration = re.compile(r"\[timer_([0-9]+)(min|sec)\]")
            #                 instance_duration = timer_duration.findall(instance_value.value)
            #                 if instance_duration:
            #                     dur_sec = instance_duration[0][0]
            #                     dur_unit = instance_duration[0][1]
            #                     if dur_unit is 'min':
            #                         dur_sec = dur_sec * 60
            #                 else:
            #                     # Default duration
            #                     dur_sec = 60


            #                 # For UHN study, record RIG answers as audio
            #                 if is_uhn_study:
            #                     requires_audio = True

            #                     # TODO: Use regex or update in DB
            #                     display_value = instance_value.value
            #                     display_value = display_value.replace('write down', 'say')

            #                     display_value = display_value.replace('in the box below', 'that come to mind randomly')

            #                     display_value = display_value.replace('Separate them with commas. Keep writing for 1 minute', 'Keep talking for 1 minute')
            #                     display_value = display_value.replace('Separate the names with commas. Keep writing for 1 minute', 'Keep talking for 1 minute')
            #                     display_value = display_value.replace('Separate the letters with commas. Keep writing for 1 minute', 'Keep talking for 1 minute')
            #                     display_value = display_value.replace('Separate the numbers with commas. Keep writing for 1 minute', 'Keep talking for 1 minute')

            #                     display_field = re.sub(timer_duration, "<br /><br />", display_value)
            #                     display_field += '''<div class='timer_display' id='timer_display_%s'>01:00</div>
            #                                         <input type='hidden' id='timer_val_%s' value='%s' />
            #                                         <input class='form-field' name='instanceid' type='hidden' value='%s' />''' % (instance_id, instance_id, dur_sec, instance_id)

            #                     response_field = ""
            #                     response_field += "<p id='record-btn_" + instance_id + "'"
            #                     response_field += "><input id='btn_recording_" + instance_id + "' type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: toggleRecordingRig(this); startTimerRigAudio(this, " + instance_id + ");' value='Start recording'>&nbsp;<span class='invisible' id='status_recording_" + instance_id + "'><img src='" + STATIC_URL + "img/ajax_loader.gif' /> <span id='status_recording_" + instance_id + "_msg'></span></span><input class='form-field' type='hidden' id='response_audio_" + instance_id + "' name='response_audio_" + instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' /></p>"

            #                 else:
            #                     display_field = re.sub(timer_duration, "<br /><br /><button type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: startTimerRig(this, " + instance_id + ");'>Start Timer</button><br />", instance_value.value)
            #                     # Associated textarea where the user will type out the RIG response
            #                     display_field += "<div class='timer_display' id='timer_display_" + instance_id + "'>01:00</div><input type='hidden' id='timer_val_" + instance_id + "' value='" + dur_sec + "' /><textarea class='form-control form-field input-disabled' name='response' readonly='readonly' style=\"" + style_attributes + "\"></textarea><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"


            #             elif field_data_type == "text_newlines":
            #                 sents = instance_value.value.split(" || ")
            #                 regex_nonalpha = re.compile(r"^[^a-zA-Z0-9]+$")
            #                 display_field = "<br>".join([sent[0].lower() + sent[1:] for sent in sents if not regex_nonalpha.findall(sent)])
            #             elif field_data_type == "text_stroop":
            #                 # Each instance should be displayed on its own, serially, with JS 'next' buttons in between
            #                 # HTML/JS: Display each instance in a div with class 'invisible', and add a JS function on 'next' button click
            #                 # which would hide the current div and display the next. If there is no next div, stop the audio recording
            #                 # and make the submit button active.

            #                 # Since this is a Stroop task, determine the colour in which the word stimulus should be displayed
            #                 word_stimulus,colour_stimulus = instance_value.value.split("|")
            #                 colour_hex = colour_lookup[colour_stimulus]

            #                 append_audio_response = ""
            #                 if count_inst+1 < len(active_task_instance_values):
            #                     next_instance_id = str(active_task_instance_values[count_inst+1].session_task_instance.session_task_instance_id)
            #                     if next_instance_id:
            #                         append_audio_response = "<div class='invisible status_recording' style='margin-top: 5px;'><img src='" + STATIC_URL + "img/ajax_loader.gif' /> <span class='status_recording_msg small'></div><input class='form-field' type='hidden' id='response_audio_" + next_instance_id + "' name='response_audio_" + next_instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + next_instance_id + "' />"

            #                 serial_startslide += "<div class='invisible stroop-slide'><div style='font-size: 72px; font-weight: bold; color: #" + colour_hex + ";'>" + word_stimulus.upper() + "</div><button type='button' class='btn btn-success btn-med btn-fixedwidth recording' onClick='javascript: stroopTaskNextItem(this);'>Next</button>" + append_audio_response + "</div>"
            #             else:
            #                 display_field = instance_value.value.replace('\n', '<br>')


            #             # Find associated response field data type

            #             if not instance_value.task_field.embedded_response:
            #                 response_field = Session_Response.objects.filter(session_task_instance=instance_value.session_task_instance)[0]
            #                 if response_field.date_completed:
            #                     existing_responses = True

            #                 input_field = Task_Field.objects.get(task=active_task, field_type__name='input', assoc=instance_value.task_field)
            #                 field_data_type = input_field.field_data_type.name

            #                 # Construct style attributes string from the specified field data attributes
            #                 field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=input_field)
            #                 style_attributes = ";".join([str(attr.name) + ": " + str(attr.value) for attr in field_data_attributes])

            #                 # regex for field data type 'scale' (scale_{from}_{to})
            #                 regex_scale = re.compile(r'scale\_([0-9]+)\_([0-9]+)')

            #                 if field_data_type == "multiselect":
            #                     existing_value = ""
            #                     if response_field.value_text:
            #                         existing_value = response_field.value_text
            #                     response_field = "<input class='form-field form-control' name='response' type='text' value='" + existing_value + "'><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
            #                 elif field_data_type == "text":
            #                     existing_value = ""
            #                     if response_field.value_text:
            #                         existing_value = response_field.value_text
            #                     response_field = "<input class='form-field form-control' name='response' type='text' value='" + existing_value + "' style=\"" + style_attributes + "\"><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
            #                 elif field_data_type == "textarea":
            #                     existing_value = ""
            #                     if response_field.value_text:
            #                         existing_value = response_field.value_text
            #                     response_field = "<textarea class='form-field form-control' name='response' style=\"" + style_attributes + "\">" + existing_value + "</textarea><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
            #                 elif field_data_type == "audio":
            #                     requires_audio = True

            #                     # If the display field is to be kept visible during the audio the subject provides, keep it visible and directly show a recording button
            #                     keep_visible = instance_value.task_field.keep_visible
            #                     response_field = ""
            #                     if not keep_visible:
            #                         response_field += "<p><input class='btn btn-primary btn-med btn-fixedwidth' type='button' onClick='javascript: hideDisplay(this);' value='Continue'></p>"
            #                     response_field += "<p id='record-btn_" + instance_id + "'"
            #                     if not keep_visible:
            #                         response_field += " class='invisible'"
            #                     response_field += "><input id='btn_recording_" + instance_id + "' type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: toggleRecording(this);' value='Start recording'>&nbsp;<span class='invisible' id='status_recording_" + instance_id + "'><img src='" + STATIC_URL + "img/ajax_loader.gif' /> <span id='status_recording_" + instance_id + "_msg'></span></span><input class='form-field' type='hidden' id='response_audio_" + instance_id + "' name='response_audio_" + instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' /></p>"

            #                 elif field_data_type == "select":
            #                     existing_value = ""
            #                     if response_field.value_text:
            #                         existing_value = response_field.value_text
            #                     response_field = ""

            #                     # Get associated values for the select options.
            #                     sel_options = Session_Task_Instance_Value.objects.filter(session_task_instance=instance_value.session_task_instance,task_field__field_type__name='input').order_by('session_task_instance_value_id')

            #                     for sel_option in sel_options:
            #                         response_field += "<div class='radio'>"
            #                         response_field += "<label><input type='radio' class='form-field' name='response_" + instance_id + "' value='" + sel_option.value + "'"

            #                         # Mark any previously-submitted responses as selected
            #                         if existing_value == sel_option.value:
            #                             response_field += " selected='selected'"

            #                         response_field += "> " + sel_option.value_display + "</label>"
            #                         response_field += "</div>"

            #                     response_field += "<input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"

            #                 elif regex_scale.findall(field_data_type):
            #                     matches = regex_scale.findall(field_data_type)
            #                     scale_start = matches[0][0]
            #                     scale_end = matches[0][1]

            #                     response_field = "<div class='row'><div class='col-xs-6'><div class='scale_" + str(scale_start) + "_" + str(scale_end) + "' style=\"" + style_attributes + "\"></div><div class='scale_display' style='font-size: 20px;'></div><input class='form-field' name='response' type='hidden' value='' /></div></div><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"

            #             # For picture description, display 'Record' button before image
            #             if active_task.name_id == 'picture_description':
            #                 active_instances += [response_field + "<br/>" + display_field]
            #             else:
            #                 active_instances += [display_field + "<br/>" + response_field]
            #             count_inst += 1

            # else:
            #     # The session has been completed. Display a summary.
            #     summary_tasks = Session_Task.objects.filter(session=session).order_by('order')
            #     counter = 1
            #     for next_task in summary_tasks:
            #         next_task_instances = Session_Task_Instance.objects.filter(session_task=next_task).aggregate(count_instances=Count('session_task_instance_id'))
            #         session_summary += "<tr><td>" + str(counter) + "</td><td>" + next_task.task.name + "</td><td>" + str(next_task_instances['count_instances']) + "</td></tr>"
            #         counter += 1

            # passed_vars = {
            #     'session': session, 'num_current_task': num_current_task, 'num_tasks': num_tasks,
            #     'percentage_completion': min(100,round(num_current_task*100.0/num_tasks)),
            #     'active_task': active_task, 'active_session_task_id': active_session_task_id,
            #     'serial_instances': serial_instances, 'serial_startslide': serial_startslide,
            #     'active_instances': active_instances, 'requires_audio': requires_audio,
            #     'existing_responses': existing_responses, 'completed_date': completed_date,
            #     'session_summary': session_summary, 'display_thankyou': display_thankyou,
            #     'user': request.user, 'is_authenticated': is_authenticated,
            #     'consent_submitted': consent_submitted, 'demographic_submitted': demographic_submitted,
            #     'active_notifications': active_notifications,
            #     'session_in_progress': session_in_progress
            # }