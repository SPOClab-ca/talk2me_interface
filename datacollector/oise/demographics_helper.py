"""
    Helper functions for retrieving demographics information
"""

import datetime

from datacollector.models import Demographics_Oise, Gender, Subject, Subject_Language_Oise
from constants import yes_no_map

def update_demographics(request):
    """
        Update demographics information.
    """

    if request.POST:
        if 'form_type' in request.POST and \
            request.POST['form_type'] == 'demographic_oise':

            form_values = {}
            has_errors = False
            demographics_type = None
            demographics_submitted = False

            if request.POST['form_type_demographics'] == 'general':
                form_errors = update_demographics_general(request)

                # After asking general questions, we ask questions about language
                demographics_type = 'language'
            elif request.POST['form_type_demographics'] == 'language':
                demographics_type = 'other_languages'
                demographics_submitted, form_errors = update_demographics_language(request)
            elif request.POST['form_type_demographics'] == 'other_languages':
                demographics_submitted, form_errors = update_demographics_other_languages(request)

        if form_errors:
            has_errors = True
            form_values = request.POST
            demographics_submitted = False

            # If errors in form, don't update the demographics type
            demographics_type = request.POST['form_type_demographics']
        if demographics_submitted:
            today = datetime.datetime.now()
            Subject.objects.filter(user_id=request.user.id)\
                   .update(date_demographics_submitted=today)

        return form_errors, has_errors, form_values, demographics_type, demographics_submitted

def update_demographics_general(request):
    subject = Subject.objects.get(user_id=request.user.id)
    form_errors = []

    if 'name' in request.POST and request.POST['name']:
        age = request.POST['name']
    else:
        form_errors += ['You did not enter your name.']
    if 'age' in request.POST and request.POST['age']:
        age = request.POST['age']
        try:
            int(age)
        except ValueError:
            form_errors += ['Your age should be a number.']
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
    else:
        form_errors += ['You did not specify your gender.']

    if 'identity' in request.POST:
        identity_value = request.POST['identity']
        identity = yes_no_map[identity_value]
    else:
        form_errors += ['You did not specify if you identify as First Nations, Metis, or Inuit.']

    if 'canada' in request.POST:
        canada_value = request.POST['canada']
        is_born_canada = yes_no_map[canada_value]
    else:
        form_errors += ['You did not specify if you were born in Canada.']

    if not form_errors:
        subject = Subject.objects.get(user_id=request.user.id)
        if not subject:
            form_errors += ['There was an error submitting your responses.']
            return form_errors
        else:
            Subject.objects.filter(user_id=request.user.id) \
                   .update(gender=gender)
            Demographics_Oise.objects \
                             .create(subject=subject, \
                                     gender=gender, \
                                     age=age, \
                                     grade=grade, \
                                     canada=is_born_canada, \
                                     english_ability=None, \
                                     identity=identity)
    return form_errors

def update_demographics_language(request):
    """
        Update demographics language information
        (i.e., English-speakiing ability and other languages)
    """
    subject = Subject.objects.get(user_id=request.user.id)
    form_errors = []

    if 'english' in request.POST:
        english_ability = request.POST['english']
    else:
        form_errors += ['You did not specify your English ability.']

    if 'other_languages' in request.POST:
        other_languages_value = request.POST['other_languages']
        speaks_other_languages = yes_no_map[other_languages_value]
    else:
        form_errors += ['You did not specify if you speak other languages.']

    if not form_errors:
        subject = Subject.objects.get(user_id=request.user.id)
        if not subject:
            form_errors += ['There was an error submitting your responses.']
            return form_errors
        else:
            Demographics_Oise.objects \
                             .update(english_ability=english_ability, \
                                     other_languages=speaks_other_languages)
            if speaks_other_languages:
                demographics_submitted = False
            else:
                demographics_submitted = True

    return demographics_submitted, form_errors

def update_demographics_other_languages(request):
    """
        If user checks yes on previous question, ask
        for language ability for each additional language.
    """
    subject = Subject.objects.get(user_id=request.user.id)
    form_errors = []
    demographics_submitted = False

    if 'num_other_languages' in request.POST:
        num_languages = int(request.POST['num_other_languages'])
        for i in range(1, num_languages + 1):
            if 'other_language' + str(i) + '_name' in request.POST:
                other_language_name = request.POST.get('other_language' + str(i) + '_name')
                other_language_level = request.POST.get('other_language' + str(i))

                if other_language_name and other_language_level:
                    demographics_oise = Demographics_Oise.objects.filter(subject=subject)
                    if demographics_oise:
                        demographics_oise = demographics_oise[0]
                        Subject_Language_Oise.objects.create(name=other_language_name, \
                                                            level=other_language_level, \
                                                            demographics_id=demographics_oise.id)
                        demographics_submitted = True
                    else:
                        form_errors += ['There was an error updating ' + other_language_name]
                else:
                    form_errors += ['Something went wrong.']

    else:
        form_errors += ['Something went wrong.']

    if form_errors:
        demographics_submitted = False
    return demographics_submitted, form_errors

def skip_demographics(request):
    """
        Set demographics submitted date to today
    """
    today = datetime.datetime.now()
    Subject.objects.filter(user_id=request.user.id)\
           .update(date_demographics_submitted=today)
