""" Helper functions for session. """

import re
import copy
import datetime

from csc2518.settings import STATIC_URL
from datacollector.models import Session_Response, Session_Task, Session_Task_Instance, Session_Task_Instance_Value, Task_Field, Task_Field_Data_Attribute


def get_active_task(session):
    """
    Return active task, i.e. task with lowest order and whose completed date is null.
        :param session:
    """
    active_task = Session_Task.objects.filter(session=session, \
                                              date_completed__isnull=True).order_by('order')
    if active_task:
        return active_task[0]
    else:
        return None

def get_active_task_instances(session, active_task):
    """
    Return active task instances.
        :param session:
        :param active_task:
    """
    active_task_instance_values = Session_Task_Instance_Value\
                                  .objects.filter(session_task_instance__session_task__session=session, \
                                                  session_task_instance__session_task__task=active_task.task, \
                                                  task_field__field_type__name='display')\
                                  .order_by('session_task_instance','task_field')

    return active_task_instance_values

def get_display(active_task, instance_value):
    """
    Return HTML object of display field.
        :param active_task:
        :param instance_value:
    """
    field_data_type = instance_value.task_field.field_data_type.name
    field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=instance_value.task_field)
    style_attributes = ";".join([str(attr.name) + ": " + str(attr.value) for attr in field_data_attributes])
    instance_id = str(instance_value.session_task_instance.session_task_instance_id)

    display_field = ""
    response_field = ""
    if field_data_type == "text":
        display_field = instance_value.value.replace('\n', '<br>')
    elif field_data_type == "text_well":
        display_field = "<div class='well well-lg space-bottom-small'>" + instance_value.value.replace('\n', '<br>') + "</div>"
    elif field_data_type == "image":
        display_field = "<img src='" + STATIC_URL + "img/" + instance_value.value + "' style=\"" + style_attributes + "\" />"
    elif field_data_type == "text_withblanks":
        display_field = (instance_value.value).replace("[BLANK]", "<input class='form-field' name='response' type='text' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />")
    elif field_data_type == "timer_rig":

        timer_duration = re.compile(r"\[timer_([0-9]+)(min|sec)\]")
        dur_sec = 60

        ## TODO: Update task instruction for RIG
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

        response_field = "<p id='record-btn_" + instance_id + "'"
        response_field += "><input id='btn_recording_" + instance_id + "' type='button' class='btn btn-success btn-med btn-fixedwidth' onClick='javascript: toggleRecordingRig(this); startTimerRigAudio(this, " + instance_id + ");' value='Start recording'>&nbsp;<span class='invisible' id='status_recording_" + instance_id + "'><img src='" + STATIC_URL + "img/ajax_loader.gif' /> <span id='status_recording_" + instance_id + "_msg'></span></span><input class='form-field' type='hidden' id='response_audio_" + instance_id + "' name='response_audio_" + instance_id + "' value='' /><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' /></p>"
    elif field_data_type == "text_newlines":
        sents = instance_value.value.split(" || ")
        regex_nonalpha = re.compile(r"^[^a-zA-Z0-9]+$")
        display_field = "<br>".join([sent[0].lower() + sent[1:] for sent in sents if not regex_nonalpha.findall(sent)])
    else:
        display_field = instance_value.value.replace('\n', '<br>')

    # Find associated response field data type
    if not instance_value.task_field.embedded_response:
        response_field = Session_Response.objects\
                                         .filter(session_task_instance=instance_value.session_task_instance)[0]

        input_field = Task_Field.objects\
                                .get(task=active_task, \
                                     field_type__name='input', \
                                     assoc=instance_value.task_field)
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
            sel_options = Session_Task_Instance_Value.objects\
                                                     .filter(session_task_instance=instance_value.session_task_instance, \
                                                             task_field__field_type__name='input')\
                                                     .order_by('session_task_instance_value_id')

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
        return response_field + "<br>" + display_field
    else:
        return display_field + "<br/>" + response_field

def submit_response(request, session):
    """
    Save responses to DB.
        :param request:
        :param session:
    """
    form_errors = []
    json_data = {}
    json_data["status"] = "fail"

    active_task = Session_Task.objects\
                              .filter(session=session, \
                                      date_completed__isnull=True)\
                              .order_by('order')
    if active_task:
        active_task = active_task[0]

        # Validate the form first
        # Determine the order of the questions associated with this task (e.g., non-select questions have 'response' fields, whereas
        # select questions have 'response_{instanceid}' fields).
        active_task_questions = Session_Task_Instance_Value.objects\
                                                           .filter(session_task_instance__session_task=active_task, \
                                                                   task_field__field_type__name='display')
        form_responses = request.POST.getlist('response')
        form_instances = request.POST.getlist('instanceid')
        responses = copy.deepcopy(form_responses)
        instances = copy.deepcopy(form_instances)
        counter_question = 0
        for question in active_task_questions:
            question_response = Task_Field.objects.get(assoc=question.task_field)

            next_instance = instances.pop(0)
            if question_response.field_data_type.name == 'select' or question_response.field_data_type.name == 'audio' or active_task.task.name_id == 'rig':
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
                if question_response.field_data_type.name == 'select' or question_response.field_data_type.name == 'audio' or active_task.task.name_id == 'rig':
                    # If the associated response field is 'select' or 'audio', then there will be 'response_{instanceid}' fields
                    audio_label = 'response_audio_' + str(next_instance)
                    if not audio_label in request.POST:
                        response_label = 'response_' + str(next_instance)
                        if response_label in request.POST:
                            next_response = request.POST[response_label]
                            instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)[0]

                            # Find the response field type for this task
                            response_data_type = Task_Field.objects\
                                                           .filter(task=instance.session_task.task,\
                                                                   field_type__name='input')[0].field_data_type

                            if response_data_type == 'select':
                                Session_Response.objects\
                                                .filter(session_task_instance=instance)\
                                                .update(value_text=next_response, \
                                                        date_completed=datetime.datetime.now())
                            else:
                                Session_Response.objects\
                                                .filter(session_task_instance=instance)\
                                                .update(value_text=next_response, \
                                                        date_completed=datetime.datetime.now())
                else:
                    # Otherwise, look for 'response' fields
                    next_response = responses.pop(0)
                    instance = Session_Task_Instance.objects\
                                                    .filter(session_task_instance_id=next_instance)[0]

                    # Find the response field type for this task
                    response_data_type = Task_Field.objects\
                                                   .filter(task=instance.session_task.task, \
                                                           field_type__name='input')[0].field_data_type

                    # Update the appropriate entry in the database (NB: 'audio' responses are not handled here; they are saved to database as soon as they are recorded, to avoid loss of data)
                    if response_data_type == 'multiselect':
                        Session_Response.objects\
                                        .filter(session_task_instance=instance)\
                                        .update(value_multiselect=next_response, \
                                                date_completed=datetime.datetime.now())
                    else:
                        Session_Response.objects\
                                        .filter(session_task_instance=instance)\
                                        .update(value_text=next_response, \
                                                date_completed=datetime.datetime.now())


            # Mark the task as submitted
            Session_Task.objects\
                        .filter(session=session, \
                                task=active_task.task)\
                        .update(date_completed=datetime.datetime.now())

            json_data['status'] = 'success'

    if form_errors:
        json_data['error'] = [dict(msg=x) for x in form_errors]
    return json_data
