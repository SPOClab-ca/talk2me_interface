from django.contrib.auth.models import User
from django.db import models
from datetime import datetime


# HELPER CLASSES (defining dropdown values) -----------------------------------

class Education_Level(models.Model):
    # the possible education levels

    def __unicode__(self):
        return str(self.name)
    
    education_level_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

class Gender(models.Model):
    # the possible values for the 'gender' attribute
    
    def __unicode__(self):
        return str(self.name)
    
    gender_id = models.CharField(max_length=1, primary_key=True)
    name = models.CharField(max_length=20)

class Language(models.Model):
    # the possible values for the spoken languages by the subject
    
    def __unicode__(self):
        return str(self.name) + " (" + str(self.iso_code) + ")"

    language_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    iso_code = models.CharField(max_length=2)

class Language_Level(models.Model):
    # the possible values for spoken language level

    def __unicode__(self):
        return str(self.name)
    
    language_level_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)


class Dementia_Type(models.Model):
    # the possible values for existing dementia diagnosis

    def __unicode__(self):
        return str(self.name)

    dementia_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)


class Ethnicity(models.Model):
    # the possible values for ethnicity origin

    def __unicode__(self):
        return str(self.name)

    ethnicity_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

class Country(models.Model):
    # the possible values for country of origin

    def __unicode__(self):
        return str(self.name)

    country_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    iso_code = models.CharField(max_length=2)

class Country_Province(models.Model):
    # the possible values for country subdivision

    def __unicode__(self):
        return str(self.name) + " (" + str(self.type_name) + ")"

    country_province_id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country)
    name = models.CharField(max_length=200)
    iso_code = models.CharField(max_length=10)
    type_name = models.CharField(max_length=50)


class Field_Type(models.Model):
    # Defines the types of fields that a task can contain
    # (e.g., display and input fields)
    
    def __unicode__(self):
        return str(self.name)
    
    field_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)    

class Field_Data_Type(models.Model):
    # Defines the types of data that a task field can contain
    # (e.g., text and image data)
    
    def __unicode__(self):
        return str(self.name)
    
    field_data_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50) 


class Value_Difficulty(models.Model):
    # each task instance value is associated with a level of difficulty; this 
    # table defines the set of possible difficulty levels.
    
    def __unicode__(self):
        return str(self.name)
    
    value_difficulty_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

# END HELPER CLASSES -------------------------------------------------------

class Subject(models.Model):
    # represents every participant in the study (the django auth module is used for
    # authentication; this table here records the demographic data that is collected
    # from each user for this study)

    def __unicode__(self):
        return "User " + str(self.user_id) + " (" + str(User.objects.get(id=self.user_id).username) + "), Gender: " + str(self.gender) + \
                ", DOB: " + str(self.dob) + ", Consent: " + str(self.consent_submitted) + \
                ", demographic submitted: " + str(self.demographic_submitted)

    user_id = models.IntegerField(primary_key=True)
    consent_submitted = models.IntegerField(default=0)
    demographic_submitted = models.IntegerField(default=0)
    preference_email_updates = models.IntegerField(default=0)
    preference_public_release = models.IntegerField(default=0)
    gender = models.ForeignKey(Gender,null=True,blank=True)
    dob = models.DateField(null=True,blank=True)
    ethnicity = models.ForeignKey(Ethnicity,null=True, blank=True)
    origin_country = models.ForeignKey(Country,null=True, blank=True)
    origin_country_province = models.ForeignKey(Country_Province,null=True, blank=True)
    education_level = models.ForeignKey(Education_Level,null=True, blank=True)

class Subject_Language(models.Model):
    # demographic data collected for the subject: the spoken languages, with 
    # ability in each

    def __unicode__(self):
        return "User " + str(self.subject.user_id) + " - " + str(self.language.name) + \
                " (" + str(self.level.name) + ")"

    subject = models.ForeignKey(Subject)
    language = models.ForeignKey(Language)
    level = models.ForeignKey(Language_Level)

class Subject_Dementia_Type(models.Model):
    # data collected for user regarding their existing diagnoses of dementia
    # The dementia type either exists in DementiaType table (in which case both 
    # the "dementia_type_id" and "dementia_type_name" fields are filled out as 
    # snapshots of the foreign key values), OR it is a new type manually entered
    # by the user (in which case "dementia_type_id" is null, and "dementia_type_name"
    # is filled out).

    def __unicode__(self):
        return "User " + str(self.subject.user_id) + " - " + str(self.dementia_type.name)

    subject = models.ForeignKey(Subject)
    dementia_type_id = models.IntegerField(null=True, blank=True)
    dementia_type_name = models.CharField(max_length=200)


class Task(models.Model):
    # represents every type of question the subjects have to answer
    # default_order = the place the question is shown in (e.g., if 1, then the
    #    question is shown first)
    # default_delay = the number of questions that are skipped before the question
    #    has to be answered (used for delayed recall questions)

    def __unicode__(self):
        return str(self.task_id) + " - " + str(self.name)

    task_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    instruction = models.TextField()
    default_num_instances = models.IntegerField(default=1)
    default_order = models.IntegerField()
    default_delay = models.IntegerField(default=0)
    default_embedded_delay = models.IntegerField(default=0)


class Task_Field(models.Model):
    # each task has one or more displayed, and one or more input fields.
    # This table defines the type of each field, and what kind of data it stores.
    
    def __unicode__(self):
        return "Task " + str(self.task.name) + ", Field " + str(self.name) + \
        " (Type: " + str(self.field_type.name) + ", Data type: " + \
        str(self.field_data_type.name) + ")"

    task_field_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    task = models.ForeignKey(Task)
    field_type = models.ForeignKey(Field_Type)
    field_data_type = models.ForeignKey(Field_Data_Type)
    embedded_response = models.IntegerField(default=0)
    keep_visible = models.IntegerField(default=1)
    generate_value = models.IntegerField(default=0)

class Task_Field_Data_Attribute(models.Model):
    # For every task field, there can be multiple style attributes
    # (used for display purposes)

    def __unicode__(self):
        return str(self.task_field) + ", Attribute " + \
        str(self.name) + ": " + \
        str(self.value)

    task_field = models.ForeignKey(Task_Field)
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=200)


class Task_Field_Value(models.Model):
    # each task can have many possible instances. this table defines the possible
    # values that a task instance can choose from (i.e., these are the values for
    # the field of type 'display').
    
    def __unicode__(self):
        return "Task " + str(self.task_field.task.name) + ", Field " + \
        str(self.task_field.name) + ", Value: " + str(self.value) + \
        " (Difficulty level: " + str(self.difficulty) + ")"
    
    task_field_value_id = models.AutoField(primary_key=True)
    task_field = models.ForeignKey(Task_Field)
    value = models.TextField()
    value_display = models.TextField(null=True, blank=True)
    difficulty = models.ForeignKey(Value_Difficulty)
    assoc = models.ForeignKey("self", null=True, blank=True)

class Session(models.Model):

    def __unicode__(self):
        return "Session for User " + str(self.subject.user_id) + ", Start date: " + \
        str(self.start_date) + ", End date: " + str(self.end_date)

    session_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

class Session_Task(models.Model):
    # order = the tasks are shown in ascending order
    # instruction_viewed = boolean (0/1), whether the question has been shown 
    #   at least once (this is used for delayed recall questions where the instruction 
    #   and the question response occur at different times)
    
    def __unicode__(self):
        return "Task " + str(self.task.name) + " (order: " + str(self.order) + \
         ", instruction viewed: " + str(self.instruction_viewed) + \
         ") in Session for User " + \
        str(self.session.subject.user_id) + ", started on " + \
        str(self.session.start_date)

    session_task_id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session)
    task = models.ForeignKey(Task)
    order = models.IntegerField()
    delay = models.IntegerField(default=0)
    embedded_delay = models.IntegerField(default=0)
    instruction_viewed = models.IntegerField(default=0)
    date_completed = models.DateField(null=True,blank=True)
    total_time = models.IntegerField(default=0)

class Session_Task_Instance(models.Model):
    
    def __unicode__(self):
        return "Instance of Task " + str(self.session_task.task.name) + \
        " (order: " + str(self.session_task.order) + \
         ", instruction viewed: " + str(self.session_task.instruction_viewed) + \
         ") in Session for User " + \
        str(self.session_task.session.subject.user_id) + ", started on " + \
        str(self.session_task.session.start_date)
    
    session_task_instance_id = models.AutoField(primary_key=True)
    session_task = models.ForeignKey(Session_Task)

class Session_Task_Instance_Value(models.Model):

    def __unicode__(self):
        return "Value " + str(self.value) + " (difficulty: " + \
         str(self.difficulty) + ") for Instance of Task " + \
        str(self.session_task_instance.session_task.task.name) + \
        " (order: " + str(self.session_task_instance.session_task.order) + \
         ", instruction viewed: " + \
         str(self.session_task_instance.session_task.instruction_viewed) + \
         ") in Session for User " + \
        str(self.session_task_instance.session_task.session.subject.user_id) + \
        ", started on " + \
        str(self.session_task_instance.session_task.session.start_date)

    session_task_instance_value_id = models.AutoField(primary_key=True)
    session_task_instance = models.ForeignKey(Session_Task_Instance)
    task_field = models.ForeignKey(Task_Field)
    value = models.TextField()
    value_display = models.TextField(null=True, blank=True)
    difficulty = models.ForeignKey(Value_Difficulty)

class Session_Response(models.Model):
    # represents every instance of a response for a task by a subject during a session

    def update_audio_file(self):
        # Delete old file from the response instance, if it exists
        #if self.value_audio:
        #    self.value_audio.delete()
        
        # Add the new file to the session response instance
        return self.value_audio.upload_to

    def __unicode__(self):
        response_value = "Blank"
        if self.value_text:
            response_value = self.value_text
        elif self.value_audio:
            response_value = "Audio"
        elif self.value_multiselect:
            response_value = self.value_multiselect
        
        return "Response value " + str(response_value) + " for Instance of Task " +\
            str(self.session_task_instance.session_task.task.name) + \
            " (order: " + str(self.session_task_instance.session_task.order) + \
             ", instruction viewed: " + \
             str(self.session_task_instance.session_task.instruction_viewed) + \
             ") in Session for User " + \
            str(self.session_task_instance.session_task.session.subject.user_id) + \
            ", started on " + \
            str(self.session_task_instance.session_task.session.start_date)

    session_response_id = models.AutoField(primary_key=True)
    session_task_instance = models.ForeignKey(Session_Task_Instance)
    date_completed = models.DateField(null=True,blank=True)
    value_text = models.TextField(null=True, blank=True)
    value_audio = models.FileField(null=True, \
                   blank=True, \
                   upload_to=lambda instance, filename: "datacollector/audio/" + \
                            datetime.now().strftime('%Y%m%d_%H%M%S') + "_" + \
                            str(instance.session_task_instance.session_task.session.subject.user_id) + "_" + \
                            str(instance.session_task_instance.session_task.session.session_id) + "_" + \
                            str(instance.session_task_instance.session_task_instance_id) + ".wav")
    value_multiselect = models.CommaSeparatedIntegerField(max_length=100, null=True, blank=True)

