import json
import datetime

from django.http import HttpResponse

from datacollector.models import Demographics_Oise, Gender, Subject

def update_demographics(request):
    subject = Subject.objects.get(user_id=request.user.id)

    form_values = {}
    has_errors = False
    error_messages = None
    if request.POST:
        if 'form_type' in request.POST and \
            request.POST['form_type'] == 'demographic_oise':

            form_errors = []
            yes_no_map = {
                'yes': 1,
                'no': 0,
                'idk': -1
            }

            if 'age' in request.POST and request.POST['age']:
                age = request.POST['age']
            else:
                form_errors += ['You did not enter your age.']

            if 'grade' in request.POST:
                grade = request.POST['grade']
            else:
                form_errors += ['You did not specify your grade.']

            if 'gender' in request.POST:
                map_gender_value_to_id = {
                    'female': 'f',
                    'male': 'm',
                    'nb': 'o'
                }
                gender_value = request.POST['gender']
                gender_id = map_gender_value_to_id[gender_value]
                gender = Gender.objects.get(gender_id=gender_id)
                gender_name = 'non-binary' if gender_value == 'o' else ''
            else:
                form_errors += ['You did not specify your gender.']

            if 'iep' in request.POST:
                iep_value = request.POST['iep']
                iep = yes_no_map[iep_value]
            else:
                form_errors += ['You did not specify if you have an IEP (Individual Education Plan).']

            if 'canada' in request.POST:
                canada_value = request.POST['canada']
                is_born_canada = yes_no_map[canada_value]
            else:
                form_errors += ['You did not specify if you were born in Canada.']

            if 'language' in request.POST:
                language = request.POST['language']
                if language == 'other':
                    language = request.POST['other_language']
            else:
                form_errors += ['You did not specify your most comfortable language.']

            if 'language_speak_home' in request.POST:
                language_speak_home = request.POST['language_speak_home']
            else:
                form_errors += ['You did not specify what language you mostly speak at home.']

            if 'language_hear_home' in request.POST:
                language_hear_home = request.POST['language_hear_home']
            else:
                form_errors += ['You did not specify what language you mostly hear at home.']

            missed_reading_agreement_questions = False
            if 'reading_enjoy' in request.POST:
                reading_enjoy = request.POST['reading_enjoy']
            else:
                missed_reading_agreement_questions = True
            if 'reading_time' in request.POST:
                reading_time = request.POST['reading_time']
            else:
                missed_reading_agreement_questions = True
            if 'reading_talking' in request.POST:
                reading_talking = request.POST['reading_talking']
            else:
                missed_reading_agreement_questions = True
            if 'reading_present' in request.POST:
                reading_present = request.POST['reading_present']
            else:
                missed_reading_agreement_questions = True
            if 'reading_good' in request.POST:
                reading_good = request.POST['reading_good']
            else:
                missed_reading_agreement_questions = True
            if missed_reading_agreement_questions:
                form_errors += ['You did not answer all the questions about reading.']

            missed_reading_frequency_questions = False
            if 'reading_fun' in request.POST:
                reading_fun = request.POST['reading_fun']
            else:
                missed_reading_frequency_questions = True
            if 'reading_choice' in request.POST:
                reading_choice = request.POST['reading_choice']
            else:
                missed_reading_frequency_questions = True
            if missed_reading_frequency_questions:
                form_errors += ['You did not answer all the questions about how often you read outside of school.']

        if form_errors:
            has_errors = True
            form_values = request.POST

        # Update Demographics_Oise and Subject
        else:
            subject = Subject.objects.get(user_id=request.user.id)
            if not subject:
                form_errors += ['There was an error submitting your responses.']
                return form_errors, True, request.POST
            date_submitted = datetime.datetime.now()
            Subject.objects.filter(user_id=request.user.id) \
                .update(date_demographics_submitted=date_submitted, \
                           gender=gender)
            Demographics_Oise.objects \
                             .create(subject=subject, \
                                     gender=gender, \
                                     age=age, \
                                     grade=grade, \
                                     iep=iep, \
                                     language=language, \
                                     language_speak_home=language_speak_home, \
                                     language_hear_home=language_hear_home, \
                                     reading_enjoy=reading_enjoy, \
                                     reading_time=reading_time, \
                                     reading_talking=reading_talking, \
                                     reading_present=reading_present, \
                                     reading_good=reading_good, \
                                     reading_fun=reading_fun, \
                                     reading_choice=reading_choice)
        return form_errors, has_errors, form_values