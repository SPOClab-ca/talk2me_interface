# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datacollector.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bundle',
            fields=[
                ('bundle_id', models.AutoField(serialize=False, primary_key=True)),
                ('name_id', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
                ('bundle_token', models.CharField(max_length=1000)),
                ('completion_req_sessions', models.IntegerField(null=True, blank=True)),
                ('active_enddate', models.DateField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Bundle_Task',
            fields=[
                ('bundle_task_id', models.AutoField(serialize=False, primary_key=True)),
                ('default_num_instances', models.IntegerField(default=1, null=True, blank=True)),
                ('bundle', models.ForeignKey(to='datacollector.Bundle')),
            ],
        ),
        migrations.CreateModel(
            name='Bundle_Task_Field_Value',
            fields=[
                ('bundle_task_field_value_id', models.AutoField(serialize=False, primary_key=True)),
                ('bundle_task', models.ForeignKey(to='datacollector.Bundle_Task')),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('client_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('secret', models.CharField(max_length=1000)),
                ('secret_expirydate', models.DateTimeField(null=True, blank=True)),
                ('datetime_created', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClientType',
            fields=[
                ('clienttype_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('country_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('iso_code', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Country_Province',
            fields=[
                ('country_province_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('iso_code', models.CharField(max_length=10)),
                ('type_name', models.CharField(max_length=50)),
                ('country', models.ForeignKey(to='datacollector.Country')),
            ],
        ),
        migrations.CreateModel(
            name='Dementia_Type',
            fields=[
                ('dementia_type_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('ranking', models.IntegerField()),
                ('requires_detail', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Education_Level',
            fields=[
                ('education_level_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('ranking', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Ethnicity',
            fields=[
                ('ethnicity_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('ranking', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Field_Data_Type',
            fields=[
                ('field_data_type_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Field_Type',
            fields=[
                ('field_type_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('gender_id', models.CharField(max_length=1, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('ranking', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('language_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('iso_code', models.CharField(max_length=2)),
                ('is_official', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Language_Level',
            fields=[
                ('language_level_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('ranking', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('notification_name', models.CharField(max_length=200)),
                ('notification_text', models.TextField()),
                ('notification_trigger', models.CharField(max_length=50, null=True, blank=True)),
                ('icon_filename', models.CharField(max_length=100)),
                ('notification_target', models.CharField(max_length=200, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Prize',
            fields=[
                ('prize_id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('prize_name', models.CharField(max_length=200)),
                ('prize_value', models.DecimalField(max_digits=6, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('session_id', models.AutoField(serialize=False, primary_key=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Session_Response',
            fields=[
                ('session_response_id', models.AutoField(serialize=False, primary_key=True)),
                ('date_completed', models.DateField(null=True, blank=True)),
                ('value_text', models.TextField(null=True, blank=True)),
                ('value_audio', models.FileField(null=True, upload_to=datacollector.models.generate_upload_filename, blank=True)),
                ('value_multiselect', models.CommaSeparatedIntegerField(max_length=100, null=True, blank=True)),
                ('value_expected', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Session_Task',
            fields=[
                ('session_task_id', models.AutoField(serialize=False, primary_key=True)),
                ('order', models.IntegerField()),
                ('delay', models.IntegerField(default=0)),
                ('embedded_delay', models.IntegerField(default=0)),
                ('instruction_viewed', models.IntegerField(default=0)),
                ('date_completed', models.DateField(null=True, blank=True)),
                ('total_time', models.IntegerField(default=0)),
                ('session', models.ForeignKey(to='datacollector.Session')),
            ],
        ),
        migrations.CreateModel(
            name='Session_Task_Instance',
            fields=[
                ('session_task_instance_id', models.AutoField(serialize=False, primary_key=True)),
                ('session_task', models.ForeignKey(to='datacollector.Session_Task')),
            ],
        ),
        migrations.CreateModel(
            name='Session_Task_Instance_Value',
            fields=[
                ('session_task_instance_value_id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.TextField()),
                ('value_display', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Session_Type',
            fields=[
                ('session_type_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('text_only', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('setting_name', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('setting_value', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('user_id', models.IntegerField(serialize=False, primary_key=True)),
                ('date_created', models.DateField()),
                ('date_consent_submitted', models.DateField(null=True, blank=True)),
                ('date_demographics_submitted', models.DateField(null=True, blank=True)),
                ('date_last_session_access', models.DateField(null=True, blank=True)),
                ('consent_alternate', models.IntegerField(default=0)),
                ('email_validated', models.IntegerField(default=0)),
                ('email_token', models.CharField(max_length=1000, null=True, blank=True)),
                ('preference_email_reminders', models.IntegerField(default=0)),
                ('preference_email_reminders_freq', models.IntegerField(null=True, blank=True)),
                ('email_reminders', models.CharField(max_length=100, null=True, blank=True)),
                ('preference_email_updates', models.IntegerField(default=0)),
                ('email_updates', models.CharField(max_length=100, null=True, blank=True)),
                ('preference_public_release', models.IntegerField(default=0)),
                ('preference_prizes', models.IntegerField(default=0)),
                ('email_prizes', models.CharField(max_length=100, null=True, blank=True)),
                ('dob', models.DateField(null=True, blank=True)),
                ('dementia_med', models.IntegerField(null=True, blank=True)),
                ('smoker_recent', models.IntegerField(null=True, blank=True)),
                ('auth_token', models.CharField(max_length=1000, null=True, blank=True)),
                ('auth_token_expirydate', models.DateTimeField(null=True, blank=True)),
                ('phone_pin', models.CharField(max_length=4, null=True, blank=True)),
                ('education_level', models.ForeignKey(blank=True, to='datacollector.Education_Level', null=True)),
                ('gender', models.ForeignKey(blank=True, to='datacollector.Gender', null=True)),
                ('origin_country', models.ForeignKey(related_name='subject_origin_country', blank=True, to='datacollector.Country', null=True)),
                ('origin_country_province', models.ForeignKey(blank=True, to='datacollector.Country_Province', null=True)),
                ('residence_country', models.ForeignKey(related_name='subject_residence_country', blank=True, to='datacollector.Country', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject_Bundle',
            fields=[
                ('subject_bundle_id', models.AutoField(serialize=False, primary_key=True)),
                ('active_startdate', models.DateField()),
                ('active_enddate', models.DateField(null=True, blank=True)),
                ('completion_token', models.CharField(max_length=1000, null=True, blank=True)),
                ('completion_token_usedate', models.DateField(null=True, blank=True)),
                ('completion_req_sessions', models.IntegerField(null=True, blank=True)),
                ('bundle', models.ForeignKey(to='datacollector.Bundle')),
                ('subject', models.ForeignKey(to='datacollector.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='Subject_Dementia_Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dementia_type_id', models.IntegerField(null=True, blank=True)),
                ('dementia_type_name', models.CharField(max_length=200)),
                ('subject', models.ForeignKey(to='datacollector.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='Subject_Emails',
            fields=[
                ('email_id', models.IntegerField(serialize=False, primary_key=True)),
                ('date_sent', models.DateField()),
                ('email_from', models.CharField(max_length=100)),
                ('email_to', models.CharField(max_length=100)),
                ('email_type', models.CharField(max_length=50)),
                ('prize_amt', models.DecimalField(null=True, max_digits=6, decimal_places=2, blank=True)),
                ('subject', models.ForeignKey(to='datacollector.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='Subject_Ethnicity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ethnicity', models.ForeignKey(to='datacollector.Ethnicity')),
                ('subject', models.ForeignKey(to='datacollector.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='Subject_Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.ForeignKey(to='datacollector.Language')),
                ('level', models.ForeignKey(to='datacollector.Language_Level')),
                ('subject', models.ForeignKey(to='datacollector.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='Subject_Notifications',
            fields=[
                ('subject_notification_id', models.IntegerField(serialize=False, primary_key=True)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField(null=True, blank=True)),
                ('dismissed', models.IntegerField(default=0)),
                ('notification', models.ForeignKey(to='datacollector.Notification')),
                ('subject', models.ForeignKey(to='datacollector.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='Subject_Prizes',
            fields=[
                ('subject_prize_id', models.IntegerField(serialize=False, primary_key=True)),
                ('date_received', models.DateTimeField()),
                ('filename', models.CharField(max_length=200, null=True, blank=True)),
                ('prize', models.ForeignKey(to='datacollector.Prize')),
                ('subject', models.ForeignKey(to='datacollector.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='Subject_UsabilitySurvey',
            fields=[
                ('subjectsurvey_id', models.AutoField(serialize=False, primary_key=True)),
                ('question_id', models.CharField(max_length=50)),
                ('question', models.TextField()),
                ('question_type', models.CharField(max_length=50)),
                ('question_order', models.IntegerField()),
                ('response_id', models.CharField(max_length=50, null=True, blank=True)),
                ('response', models.TextField(null=True, blank=True)),
                ('date_completed', models.DateField()),
                ('subject', models.ForeignKey(to='datacollector.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('task_id', models.AutoField(serialize=False, primary_key=True)),
                ('name_id', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('instruction', models.TextField()),
                ('instruction_phone', models.TextField(null=True, blank=True)),
                ('default_num_instances', models.IntegerField(default=1, null=True, blank=True)),
                ('default_order', models.IntegerField()),
                ('is_order_fixed', models.IntegerField(default=0)),
                ('default_delay', models.IntegerField(default=0)),
                ('default_embedded_delay', models.IntegerField(default=0)),
                ('is_active', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Task_Field',
            fields=[
                ('task_field_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('embedded_response', models.IntegerField(default=0)),
                ('keep_visible', models.IntegerField(default=1)),
                ('generate_value', models.IntegerField(default=0)),
                ('default_num_instances', models.IntegerField(null=True, blank=True)),
                ('preserve_order', models.IntegerField(null=True, blank=True)),
                ('assoc', models.ForeignKey(blank=True, to='datacollector.Task_Field', null=True)),
                ('field_data_type', models.ForeignKey(to='datacollector.Field_Data_Type')),
                ('field_type', models.ForeignKey(to='datacollector.Field_Type')),
                ('task', models.ForeignKey(to='datacollector.Task')),
            ],
        ),
        migrations.CreateModel(
            name='Task_Field_Data_Attribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('value', models.CharField(max_length=200)),
                ('task_field', models.ForeignKey(to='datacollector.Task_Field')),
            ],
        ),
        migrations.CreateModel(
            name='Task_Field_Value',
            fields=[
                ('task_field_value_id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.TextField()),
                ('value_display', models.TextField(null=True, blank=True)),
                ('response_expected', models.TextField(null=True, blank=True)),
                ('assoc', models.ForeignKey(blank=True, to='datacollector.Task_Field_Value', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Value_Difficulty',
            fields=[
                ('value_difficulty_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='task_field_value',
            name='difficulty',
            field=models.ForeignKey(to='datacollector.Value_Difficulty'),
        ),
        migrations.AddField(
            model_name='task_field_value',
            name='task_field',
            field=models.ForeignKey(to='datacollector.Task_Field'),
        ),
        migrations.AddField(
            model_name='session_task_instance_value',
            name='difficulty',
            field=models.ForeignKey(to='datacollector.Value_Difficulty'),
        ),
        migrations.AddField(
            model_name='session_task_instance_value',
            name='session_task_instance',
            field=models.ForeignKey(to='datacollector.Session_Task_Instance'),
        ),
        migrations.AddField(
            model_name='session_task_instance_value',
            name='task_field',
            field=models.ForeignKey(to='datacollector.Task_Field'),
        ),
        migrations.AddField(
            model_name='session_task',
            name='task',
            field=models.ForeignKey(to='datacollector.Task'),
        ),
        migrations.AddField(
            model_name='session_response',
            name='session_task_instance',
            field=models.ForeignKey(to='datacollector.Session_Task_Instance'),
        ),
        migrations.AddField(
            model_name='session',
            name='session_type',
            field=models.ForeignKey(to='datacollector.Session_Type'),
        ),
        migrations.AddField(
            model_name='session',
            name='subject',
            field=models.ForeignKey(to='datacollector.Subject'),
        ),
        migrations.AddField(
            model_name='client',
            name='clienttype',
            field=models.ForeignKey(to='datacollector.ClientType'),
        ),
        migrations.AddField(
            model_name='bundle_task_field_value',
            name='task_field_value',
            field=models.ForeignKey(to='datacollector.Task_Field_Value'),
        ),
        migrations.AddField(
            model_name='bundle_task',
            name='task',
            field=models.ForeignKey(to='datacollector.Task'),
        ),
    ]
