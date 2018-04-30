"""
    Helper functions for retrieving demographics information
"""

from datacollector.models import Questionnaire_Oise, Session
from datacollector.oise.constants import yes_no_map

def save_questionnaire_responses(request):
    """
        Save questionnaire responses
    """

    form_values = {}
    form_errors = []
    if request.POST:
        if 'form_type' in request.POST and \
            request.POST['form_type'] == 'questionnaire':
            questionnaire_responses = {}

            response_types = ['enjoy_reading', 'fun_reading', 'good_reader', \
                              'ease_reading', 'long_reading', 'challenging_reading', \
                              'iep', 'esl']
            error_messages = ['You did not specify if you enjoy reading.', \
                              'You did not specify if you like to read for fun', \
                              'You did not specify if you are a good reader.', \
                              'You did not specify if reading is easy for you.', \
                              'You did not specify if you like to read long texts.', \
                              'You did not specify if you like reading challenging texts.', \
                              'You did not specify if you have an IEP.', \
                              'You did not specify if you have taken an ESL class.']

            for response_type, error_message in zip(response_types, error_messages):
                if response_type in request.POST and request.POST[response_type]:
                    if response_type in ['iep', 'esl']:
                        response = request.POST[response_type]
                        response_value = yes_no_map[response]
                        questionnaire_responses[response_type] = response_value
                    else:
                        questionnaire_responses[response_type] = int(request.POST[response_type])
                else:
                    form_errors += [error_message]
        else:
            form_errors += ['There was an error retrieving your responses.']

        if form_errors:
            form_values = request.POST
        else:
            session_id = int(request.POST['session_id'])
            session = Session.objects.get(session_id=session_id)
            qr = questionnaire_responses
            Questionnaire_Oise.objects\
                              .create(session=session, \
                                      enjoy_reading=qr['enjoy_reading'], \
                                      fun_reading=qr['fun_reading'], \
                                      good_reader=qr['good_reader'], \
                                      ease_reading=qr['ease_reading'], \
                                      long_reading=qr['long_reading'], \
                                      challenging_reading=qr['challenging_reading'], \
                                      iep=qr['iep'], \
                                      esl=qr['esl'])

        return form_errors, form_values
