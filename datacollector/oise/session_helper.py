"""
    Helper functions for Session.
"""

import re
import copy
import datetime
import urllib

from csc2518.settings import STATIC_URL
from django.core.files.base import ContentFile
from datacollector.models import Bundle, Bundle_Task, Bundle_Task_Field_Value, Field_Type, Session, Session_Response, \
                                 Session_Task, Session_Task_Instance, \
                                 Session_Task_Instance_Value, Task, Task_Field, Task_Field_Data_Attribute, Task_Field_Value

from constants import MINDMAP_HTML, DEFAULT_MINDMAP_IMAGE, MINDMAP_IMAGE_LIGHT, \
                      MINDMAP_IMAGE_TIP

WORD_COMPLETION = 'word_completion_oise'
PICTURE_DESCRIPTION = 'picture_description_oise'
STORY_RETELLING = 'story_retelling_oise'
WORD_MAP = 'word_map_oise'
PUZZLE_SOLVING = 'puzzle_solving_oise'
WORD_RECALL = 'word_recall_oise'
WORD_SOUNDS = 'word_sounds_oise'

WORD_SOUNDS_TASK = Task.objects.get(name_id=WORD_SOUNDS)

FIELD_TYPE_INPUT_ID = Field_Type.objects.get(name='input')
FIELD_TYPE_DISPLAY_ID = Field_Type.objects.get(name='display')

def display_session_task_instance(session_task_id):
    """
    Update variables for displaying session task instance
        :param session_task_id:
    """

    is_last_task_instance = False
    audio_instruction_file = None
    hide_submit_button = False


    # Retrieve active task instance values
    task_id = Session_Task.objects.get(session_task_id=session_task_id) \
              .task_id
    task_name = Task.objects.get(task_id=task_id).name_id
    session_task_instances = Session_Task_Instance.objects.filter \
                             (session_task_id=session_task_id)
    session_task_instance_ids = [session_task_instance.session_task_instance_id for \
                                 session_task_instance in session_task_instances]
    session_response_objects = Session_Response.objects \
                               .filter(session_task_instance_id__in=session_task_instance_ids, date_completed__isnull=True)

    if session_response_objects:
        active_session_task_instance = session_response_objects[0]


        # Only display one Session_Response object at a time
        if task_name == 'reading_fluency':
            display_field, response_field, requires_audio, audio_instruction_file = display_reading_fluency(active_session_task_instance.session_task_instance_id)
        elif task_name == 'picture_description_oise':
            display_field, response_field, requires_audio, audio_instruction_file = display_picture_description(active_session_task_instance.session_task_instance_id)
        elif task_name == 'story_retelling_oise':
            display_field, response_field, requires_audio, audio_instruction_file = display_story_retelling(active_session_task_instance.session_task_instance_id)
        elif task_name == WORD_MAP:
            display_field, response_field, requires_audio, audio_instruction_file = display_word_map(active_session_task_instance.session_task_instance_id)
        elif task_name == PUZZLE_SOLVING:
            display_field, response_field, requires_audio, audio_instruction_file = display_puzzle_solving(active_session_task_instance.session_task_instance_id)
        elif task_name == WORD_RECALL:
            display_field, response_field, requires_audio, audio_instruction_file = display_word_recall(active_session_task_instance.session_task_instance_id)
        elif task_name == WORD_SOUNDS:
            display_field, response_field, \
                requires_audio, hide_submit_button = display_task(active_session_task_instance.session_task_instance_id,\
                                              task_id)

        if len(session_response_objects) == 1:
            is_last_task_instance = True

        return active_session_task_instance, display_field, response_field, requires_audio, is_last_task_instance, audio_instruction_file, hide_submit_button
    #else:
        # TODO: All tasks were complete???

def submit_response(request):
    """
    Submit response and save to database.
        :param request:
    """
    json_data = {}
    # Validate the form first
    # Determine the order of the questions associated with this task (e.g., non-select questions have 'response' fields, whereas
    # select questions have 'response_{instanceid}' fields).
    form_responses = request.POST.getlist('response')
    form_instances = request.POST.getlist('instanceid')
    responses = copy.deepcopy(form_responses)
    instances = copy.deepcopy(form_instances)

    if len(form_instances) > 1:
        active_task_instance_questions = Session_Task_Instance_Value.objects \
                                         .filter(session_task_instance_id__in=form_instances)
    else:
        instance_id = request.POST['instanceid']
        active_task_instance_questions = Session_Task_Instance_Value.objects \
                                        .filter(session_task_instance_id=instance_id)
    if active_task_instance_questions:
        active_task_instance_question = active_task_instance_questions[0]

    # Need to check if the Session_Task is completed
    associated_task_instances = Session_Task_Instance.objects \
                                   .filter(session_task=active_task_instance_question \
                                                        .session_task_instance \
                                                        .session_task)
    if 'isdummy' in request.POST:
        for instance in instances:
            Session_Response.objects.filter(session_task_instance=instance).update(value_text='', date_completed=datetime.datetime.now())
        incomplete_session_responses = Session_Response.objects \
                                      .filter(session_task_instance__in=associated_task_instances,
                                              date_completed__isnull=True)
        if not incomplete_session_responses:
            active_task = active_task_instance_question.session_task_instance.session_task
            Session_Task.objects.filter(session=active_task.session, task=active_task.task).update(date_completed=datetime.datetime.now())

            # Update Session if necessary
            session_tasks = Session_Task.objects.filter(session=active_task.session, date_completed__isnull=True)
            if not session_tasks:
                Session.objects.filter(session_id=active_task.session.session_id).update(end_date=datetime.datetime.now())
        json_data['status'] = 'success'
        return json_data
    question_field = Task_Field.objects \
                     .get(task_field_id=active_task_instance_question.task_field_id)
    response_field = Task_Field.objects.get(assoc_id=question_field.task_field_id)
    form_errors = []
    counter_question = 0
    # If audio, the Session_Response object will already be updated
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
                    Session_Response.objects.filter(session_task_instance=instance).update(value_text=next_response, date_completed=datetime.datetime.now())
                    if not instance:
                        form_errors += ['Question #' + str(counter_question+1) + \
                                        ' is invalid.']
                else:
                    form_errors += ['You did not provide a response for question #' + str(counter_question+1) + '.']
        elif response_field.field_data_type.name == 'text' or response_field.field_data_type.name == 'suffix_completion':
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
            if 'imageurl' in request.POST:
                image_url = request.POST['imageurl']

                instance = Session_Task_Instance.objects.filter(session_task_instance_id=next_instance)
                if instance:
                    instance = instance[0]
                    Session_Response.objects.filter(session_task_instance=instance) \
                                    .update(date_completed=datetime.datetime.now())
                    session_response = Session_Response.objects.get(session_task_instance=instance)

                    # Temporary, will need to save as value_image or value_text instead of value_audio
                    temp_filename, _ = urllib.urlretrieve(image_url)
                    file_content = ContentFile(open(temp_filename).read())
                    session_response.value_image.save('', file_content)
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
            active_task = active_task_instance_question.session_task_instance.session_task
            Session_Task.objects.filter(session=active_task.session, task=active_task.task).update(date_completed=datetime.datetime.now())
            session_task_in_progress = False

            # Update Session if necessary
            session_tasks = Session_Task.objects.filter(session=active_task.session, date_completed__isnull=True)
            if not session_tasks:
                Session.objects.filter(session_id=active_task.session.session_id).update(end_date=datetime.datetime.now())
    json_data['status'] = 'success'

    ## SUBMITTING ANSWERS
    if form_errors:
        json_data['error'] = [dict(msg=x) for x in form_errors]
        json_data['status'] = 'error'

    return json_data

def display_task(session_task_instance_id, task_id):
    """
    Generic task display
        :param session_task_instance_id:
        :param task_id:
    """
    hide_submit_button = False

    #Query task instances
    task_instance = Session_Task_Instance_Value.objects \
                    .get(session_task_instance_id=session_task_instance_id)

    if task_id == WORD_SOUNDS_TASK.task_id:
        audio_example_task_field = Task_Field.objects.get(name='word_sounds_example')
        feedback_task_field = Task_Field.objects.get(name='word_sounds_feedback')
        audio_task_field = Task_Field.objects.get(name='word_sounds_audio')
        text_instruction_task_field = Task_Field.objects.get(name='word_sounds_text_instruction')
        text_example_task_field = Task_Field.objects.get(name='word_sounds_text_example')
        text_task_field = Task_Field.objects.get(name='word_sounds_text')

        task_field = task_instance.task_field
        display_field = display_question(task_instance, str(task_field.field_data_type))
        display_only_fields = [audio_example_task_field.task_field_id, \
                               feedback_task_field.task_field_id, \
                               text_instruction_task_field.task_field_id, \
                               text_example_task_field.task_field_id]
        if task_field.task_field_id == audio_task_field.task_field_id:
            display_field = display_question(task_instance, str(task_field.field_data_type), autoplay=True)
            response = Task_Field.objects.get(assoc_id=task_field.task_field_id)
            response_field, requires_audio = display_response(task_instance, str(response.field_data_type), recording_button_text="Record")
        elif task_field.task_field_id == text_task_field.task_field_id:
            display_field = "<h1>" + task_instance.value_display + "</h1>"
            display_field += '<audio audio id="audioEl" controls controlsList="nodownload" autoplay style="display:none;">'
            display_field += '<source src="%saudio/oise/%s" type="audio/mpeg">' \
                                % (STATIC_URL, task_instance.value)
            display_field += 'Your browser does not support the audio element.</audio>'
            display_field += '<span onclick="playAudio(\'audioEl\', \'audioButton\');"> <i class="fas fa-volume-up"></i> </span>'
            response = Task_Field.objects.get(assoc_id=task_field.task_field_id, field_type_id=2)
            response_field, requires_audio = display_response(task_instance, str(response.field_data_type))
        elif task_field.task_field_id in display_only_fields:
            if "You finished the task!" in task_instance.value:
                display_field += '<audio audio id="audioEl" controls controlsList="nodownload" autoplay style="display:none;">'
                display_field += '<source src="%saudio/oise/instructions/word_sounds_finished.mp3" type="audio/mpeg">' % (STATIC_URL)
                display_field += 'Your browser does not support the audio element.</audio>'
                display_field += '<span onclick="playAudio(\'audioEl\', \'audioButton\');"> <i class="fas fa-volume-up"></i> </span>'
                reload_fn = "reloadPageOise"
                text_display = "Next"
            else:
                if task_field.task_field_id == text_instruction_task_field.task_field_id:
                    display_field += '<audio audio id="audioEl" controls controlsList="nodownload" autoplay style="display:none;">'
                    display_field += '<source src="%saudio/oise/instructions/word_sounds_text_instruction.mp3" type="audio/mpeg">' % (STATIC_URL)
                    display_field += 'Your browser does not support the audio element.</audio>'
                    display_field += '<span onclick="playAudio(\'audioEl\', \'audioButton\');"> <i class="fas fa-volume-up"></i> </span>'
                elif task_field.task_field_id == text_example_task_field.task_field_id:
                    display_field = "<h2>Let's look at an example!</h2>"
                    display_field += "<h1>" + task_instance.value_display + "</h1>"
                    display_field += display_question(task_instance, str(task_field.field_data_type), autoplay=True)
                elif task_field.task_field_id == feedback_task_field.task_field_id:
                    display_field = "<h2>Let's check the answer!</h2>"
                    display_field += display_question(task_instance, str(task_field.field_data_type), autoplay=True)
                elif task_field.task_field_id == audio_example_task_field.task_field_id:
                    display_field = "<h2>Let's hear an example!</h2>"
                    display_field += display_question(task_instance, str(task_field.field_data_type), autoplay=True)
                else:
                    display_field = display_question(task_instance, str(task_field.field_data_type), autoplay=True)
                reload_fn = "reloadPage"
                text_display = "Next"
            response_field = "<p><input class='form-field'" + \
                             " name='instanceid' type='hidden' value='" \
                             + str(session_task_instance_id) + "' />" + \
                             "<input class='btn btn-primary oise-button" + \
                             " btn-lg btn-fixedwidth' type='button'" + \
                             " onClick='javascript: submitDummyResponse(this," + reload_fn + \
                             ");' value='" + text_display + "'></p>"
            requires_audio = False
            hide_submit_button = True
        else:
            response_field = ''
            requires_audio = False
    else:
        # Get fields for question and response(s)
        question = Task_Field.objects.get(task_id=task_id, field_type_id=1)
        response = Task_Field.objects.get(task_id=task_id, field_type_id=2)

        display_field = display_question(task_instance, str(question.field_data_type))

        response_field, requires_audio = display_response(task_instance, str(response.field_data_type))


    return display_field, response_field, requires_audio, hide_submit_button


def display_reading_fluency(session_task_instance_id):
    """
    Display question field and response field for the reading
    fluency task.
        :param session_task_instance_id:
    """
    task_id = Task.objects.get(name_id='reading_fluency')
    task_instances = Session_Task_Instance_Value.objects \
                    .filter(session_task_instance_id=session_task_instance_id)

    task_field_question = Task_Field.objects.get(name='reading_fluency_question')
    task_field_story = Task_Field.objects.get(name='reading_fluency_story')
    # For stories, we only display one question field and one response field
    task_instance = task_instances[0]
    task_field_id = task_instance.task_field_id

    if task_field_id == task_field_story.task_field_id:

        response = Task_Field.objects.get(assoc_id=task_field_id)
        response_field, requires_audio = display_response(task_instance, str(response.field_data_type), \
        recording_button_text="Start reading out loud")
        audio_instruction_file = 'instructions/reading_fluency_story.mp3'

    # For multiple choice questions, we display one question field and multiple response fields
    elif task_field_id == task_field_question.task_field_id:
        audio_instruction_file = 'instructions/reading_fluency_question.mp3'
        response = Task_Field.objects.get(assoc_id=task_field_id)
        response_instances = Session_Task_Instance_Value.objects \
                                .filter(session_task_instance_id=session_task_instance_id, \
                                 task_field_id=response.task_field_id)
        response_field = ''
        for response_instance in response_instances:
            response_instance_field, _ = display_response(response_instance, \
                                                          str(response.field_data_type))
        response_field += response_instance_field

        requires_audio = False

    question = Task_Field.objects.get(task_field_id=task_field_id)
    display_field = display_question(task_instance, str(question.field_data_type))

    return display_field, response_field, requires_audio, audio_instruction_file

def display_picture_description(session_task_instance_id):
    """
    Display question field and response field the picture
    description task.
        :param session_task_instance_id:
    """
    task_id = Task.objects.get(name_id='picture_description_oise').task_id
    task_instance = Session_Task_Instance_Value.objects \
                    .get(session_task_instance_id=session_task_instance_id)
    question = Task_Field.objects.get(task_id=task_id, field_type_id=1)
    response = Task_Field.objects.get(task_id=task_id, field_type_id=2)

    display_field = display_question(task_instance, str(question.field_data_type))

    response_field, requires_audio = display_response(task_instance, \
                                                      str(response.field_data_type), \
                                                      recording_button_text="Start describing")

    audio_instruction_file = 'instructions/picture_description_picture.mp3'

    return display_field, response_field, requires_audio, audio_instruction_file

def display_story_retelling(session_task_instance_id):
    """
    Display question field and response field for story retelling
    task.
        :param session_task_instance_id:
    """
    task_id = Task.objects.get(name_id='story_retelling_oise').task_id
    story_audio_task_field = Task_Field.objects.get(name='story_audio', task_id=task_id)
    story_text_task_field = Task_Field.objects.get(name='story_text', task_id=task_id)

    task_instance = Session_Task_Instance_Value.objects \
                    .get(session_task_instance_id=session_task_instance_id)

    task_field_id = task_instance.task_field_id
    story_field = Task_Field.objects.get(task_field_id=task_field_id)

    response = Task_Field.objects.get(assoc_id=task_field_id, field_data_type=2)

    display_field = display_question(task_instance, str(story_field.field_data_type))
    if task_field_id == story_audio_task_field.task_field_id:
        audio_instruction_file = 'instructions/story_retelling_listen.mp3'
    elif task_field_id == story_text_task_field.task_field_id:
        audio_instruction_file = 'instructions/story_retelling_read.mp3'

    audio_instruction = "Retell the story with as many details as you can remember. "
    audio_instruction += "Click the <b>Start retelling</b> button below."
    show_audio_instruction_file = '%saudio/oise/instructions/story_retelling_retell.mp3' % STATIC_URL
    response_field, requires_audio = display_response(task_instance, str(response.field_data_type), \
                                                      recording_button_text="Start retelling", \
                                                      audio_instruction=audio_instruction, \
                                                      show_audio_instruction_file=show_audio_instruction_file)

    return display_field, response_field, requires_audio, audio_instruction_file

def display_word_completion(session_task_id):
    """
    Display question field and task field for word completion
    task.
        :param session_task_id:
    """
    task_id = Task.objects.get(name_id=WORD_COMPLETION).task_id
    task_instances = Session_Task_Instance.objects \
                    .filter(session_task_id=session_task_id)
    question = Task_Field.objects.get(task_id=task_id, \
                                      field_type_id=FIELD_TYPE_DISPLAY_ID)
    response = Task_Field.objects.get(task_id=task_id, \
                                      field_type_id=FIELD_TYPE_INPUT_ID)

    display_field = ''
    for idx, task_instance in enumerate(task_instances):
        task_instance_value = Session_Task_Instance_Value.objects \
                              .get(session_task_instance_id=task_instance \
                                                            .session_task_instance_id)
        display_field += ('%d. ' % (idx + 1)) + display_question(task_instance_value, str(question.field_data_type)) + '<br>'

    response_field, requires_audio = display_response(task_instance_value, str(response.field_data_type))

    return '<br>', display_field, False

def display_word_map(session_task_instance_id):
    """
    Display word map question field and response.
        :param session_task_instance_id:
    """
    task_id = Task.objects.get(name_id=WORD_MAP).task_id
    task_instance = Session_Task_Instance_Value.objects \
                    .get(session_task_instance_id=session_task_instance_id)
    question = Task_Field.objects.get(task_id=task_id, field_type_id=FIELD_TYPE_DISPLAY_ID)

    display_field = '<h2>Your target word is: <b>'
    display_field += task_instance.value
    display_field += '</b></h2>'

    if str(task_instance.value) == 'tip':
        mindmap_image_url = MINDMAP_IMAGE_TIP
    elif str(task_instance.value) == 'light':
        mindmap_image_url =  MINDMAP_IMAGE_LIGHT
    else:
        mindmap_image_url = DEFAULT_MINDMAP_IMAGE
    response_field = MINDMAP_HTML % (session_task_instance_id, mindmap_image_url)
    response_field += "<input class='form-field'" + \
                                 " name='instanceid' type='hidden' value='" \
                                 + str(session_task_instance_id) + "' />"
    response_field += "<input class='form-field'" + \
                                 " id='imageurl'"
    response_field += " name='imageurl' type='hidden' value='%s' />" \
                                 % mindmap_image_url
    response_field += "<br><br><br>"
    audio_instruction_file = 'instructions/word_map_click.mp3'

    return display_field, response_field, False, audio_instruction_file

def display_puzzle_solving(session_task_instance_id):
    task_id = Task.objects.get(name_id=PUZZLE_SOLVING).task_id

    image_field = Task_Field.objects.get(task_id=task_id, \
                                         field_type_id=FIELD_TYPE_DISPLAY_ID)
    response = Task_Field.objects.get(assoc_id=image_field.task_field_id, \
                                      field_type_id=FIELD_TYPE_INPUT_ID)

    task_instance = Session_Task_Instance_Value.objects \
                    .get(session_task_instance_id=session_task_instance_id, \
                         task_field_id=image_field.task_field_id)
    display_field = display_question(task_instance, str(image_field.field_data_type))

    response_field = ''
    response_field_instances = Session_Task_Instance_Value.objects \
                               .filter(session_task_instance_id=session_task_instance_id, \
                                task_field_id=response.task_field_id)
    for response_field_task_instance in response_field_instances:
        response_field_instance, _ = display_response(response_field_task_instance, \
                                                       str(response.field_data_type), \
                                                       is_image=True)
    response_field += response_field_instance

    audio_instruction_file = 'instructions/puzzle_solving_click.mp3'
    return display_field, response_field, False, audio_instruction_file

def display_word_recall(session_task_instance_id):
    task_id = Task.objects.get(name_id=WORD_RECALL).task_id

    question = Task_Field.objects.get(task_id=task_id, \
                                      field_type_id=FIELD_TYPE_DISPLAY_ID, \
                                      generate_value=1)
    task_instance = Session_Task_Instance_Value.objects \
                    .get(session_task_instance_id=session_task_instance_id, \
                         task_field_id=question.task_field_id)
    display_field = display_question(task_instance, str(question.field_data_type), autoplay=True)

    response = Task_Field.objects.get(assoc_id=question.task_field_id, \
                                      field_type_id=FIELD_TYPE_INPUT_ID)
    response_field, _ = display_response(task_instance, \
                                         str(response.field_data_type), \
                                         audio_instruction="Say as many words as you can remember!")

    # audio_instruction_file = 'instructions/word_recall_click.mp3'
    return display_field, response_field, True, None

def display_question(instance_value, field_data_type, autoplay=False):
    """
    Determine how to display the value based on the field type and construct style attributes string from the specified field
    data attributes
        :param instance_value:
        :param field_data_type:
    """

    display_field = ""
    field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=instance_value.task_field)
    style_attributes = ";".join([str(attr.name) + ": " + str(attr.value) for attr in field_data_attributes])

    session_task_instance = instance_value.session_task_instance
    instance_id = str(instance_value.session_task_instance.session_task_instance_id)

    if field_data_type == "text":
        display_field = instance_value.value.replace('\n', '<br>')
    elif field_data_type == "text_well":
        display_field = "<div class='well well-lg space-bottom-small'><h3>" + instance_value.value.replace('\n', '<br>') + "</h3></div>"
    elif field_data_type == "image":
        display_field = "<img class=\"oise-picture-description\" src='" + \
                        STATIC_URL + "img/" + instance_value.value + \
                        "' style=\"" + style_attributes + "\" />"
    elif field_data_type == "text_withblanks":
        display_field = (instance_value.value)\
                        .replace("[BLANK]", \
                                 "<input class='form-field' " + \
                                 "name='response' type='text' " + \
                                 "value='' /><input class='form-field'" + \
                                 " name='instanceid' type='hidden' value='" \
                                 + instance_id + "' />")
    elif field_data_type == "text_newlines":
        sents = instance_value.value.split(" || ")
        regex_nonalpha = re.compile(r"^[^a-zA-Z0-9]+$")
        display_field = "<br>".join([sent[0].lower() + sent[1:] for sent in sents if not regex_nonalpha.findall(sent)])
    elif field_data_type == "text_read_aloud":
        display_field = instance_value.value.replace('\n', '<br>')
        display_field += '[TO BE READ ALOUD]'
    elif field_data_type == "word_map":
        display_field = '<h2>' + instance_value.value + '</h2>'
        display_field += "<input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"
    elif field_data_type == "audio":
        if autoplay:
            display_field = '<audio id="audioEl" controls controlsList="nodownload" autoplay style="display:none;">'
            display_field += '<source src="%saudio/oise/%s" type="audio/mpeg">' \
                                % (STATIC_URL, instance_value.value)
            display_field += 'Your browser does not support the audio element.</audio>'
            display_field += '<span onclick="playAudio(\'audioEl\');" id="audioButton"><i class="fas fa-volume-up"></i> </span>'
        else:
            display_field = '<audio id="audioEl" controls controlsList="nodownload" style="display:none;">'
            display_field += '<source src="%saudio/oise/%s" type="audio/mpeg">' \
                                % (STATIC_URL, instance_value.value)
            display_field += 'Your browser does not support the audio element.</audio>'
            display_field += '<div onclick="playAudio(\'audioEl\', \'audioButton\');" class="btn btn-success oise-button btn-lg btn-fixedwidth" id="audioButton">Start listening <i class="fas fa-volume-up"></i> </div>'
    else:
        display_field = instance_value.value.replace('\n', '<br>')

    return display_field

def display_response(instance_value, field_data_type, \
                     audio_instruction=None, recording_button_text=None, \
                     show_audio_instruction_file=None, is_image=False):
    requires_audio = False
    response_field = ""
    response_object = Session_Response.objects.filter(session_task_instance=instance_value.session_task_instance)[0]
    instance_id = str(instance_value.session_task_instance_id)
    # Construct style attributes string from the specified field data attributes
    field_data_attributes = Task_Field_Data_Attribute.objects.filter(task_field=instance_value.task_field)
    if field_data_type == "audio":
        requires_audio = True

        # If the display field is to be kept visible during the audio the subject provides, keep it visible and directly show a recording button
        keep_visible = instance_value.task_field.keep_visible
        response_field = ""
        if not keep_visible:
            response_field += "<p><input class='btn btn-primary oise-button" + \
                              " btn-lg btn-fixedwidth' type='button'"
            if audio_instruction:
                response_field += " onClick='javascript: hideDisplayOise(this, \"" + \
                                    audio_instruction
                if show_audio_instruction_file:
                    response_field += "\", \"" + show_audio_instruction_file
                response_field += "\");'"
            else:
                response_field += " onClick='javascript: hideDisplayOise(this);'"
            response_field += " value='Continue'></p>"
        response_field += "<p id='record-btn_" + instance_id + "'"
        if not keep_visible:
            response_field += " class='invisible'"
        response_field += "><input id='btn_recording_" + instance_id + \
                          "' type='button' class='btn btn-success btn-lg" + \
                          " btn-fixedwidth' onClick='javascript: toggleRecording(this);'"
        if recording_button_text:
            response_field += " value='" + recording_button_text + "'>&nbsp;"
        else:
            response_field += " value='Start recording'>&nbsp;"
        response_field += "<span class='invisible' id='status_recording_" + \
                          instance_id + "'><img src='" + STATIC_URL + \
                          "img/ajax_loader.gif' /> <span id='status_recording_" + \
                          instance_id + "_msg'></span></span>" + \
                          "<input class='form-field' type='hidden' id='response_audio_" + \
                          instance_id + "' name='response_audio_" + instance_id + \
                          "' value='' /><input class='form-field' name='instanceid' " + \
                          "type='hidden' value='" + instance_id + "' /></p>"
    elif field_data_type == "select":
        existing_value = ""
        if response_object.value_text:
            existing_value = response_object.value_text
        response_field = ""

        # Get associated values for the select options.
        sel_options = Session_Task_Instance_Value.objects\
                      .filter(session_task_instance=instance_value.\
                                                    session_task_instance, \
                              task_field__field_type__name='input')\
                      .order_by('session_task_instance_value_id')

        for sel_option in sel_options:

            if is_image:
                response_field += "<div class='radio-inline'>"
                response_field += "<label><input type='radio' class='form-field' name='response_" + instance_id + "' value='" + sel_option.value + "'>"
                response_field += "<img src='%simg/" % STATIC_URL
                response_field += sel_option.value_display + "' style='width:100px;'></label>&nbsp;"
            else:
                response_field += "<div class='radio'>"
                response_field += "<label><h3><input type='radio' class='form-field' name='response_" + instance_id + "' value='" + sel_option.value + "'"
                # Mark any previously-submitted responses as selected
                if existing_value == sel_option.value:
                    response_field += " selected='selected'"
                response_field += "> " + sel_option.value_display + "</h3></label>"
            response_field += "</div>"

        response_field += "<br><input class='form-field' name='instanceid' type='hidden' value='" + instance_id + "' />"

    return response_field, requires_audio