# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datacollector', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Demographics_Oise',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('age', models.IntegerField(null=True, blank=True)),
                ('grade', models.IntegerField(null=True, blank=True)),
                ('iep', models.IntegerField(null=True, blank=True)),
                ('canada', models.IntegerField(null=True, blank=True)),
                ('language', models.CharField(max_length=100, null=True, blank=True)),
                ('language_speak_home', models.CharField(max_length=100, null=True, blank=True)),
                ('language_hear_home', models.CharField(max_length=100, null=True, blank=True)),
                ('reading_enjoy', models.IntegerField(null=True, blank=True)),
                ('reading_time', models.IntegerField(null=True, blank=True)),
                ('reading_talking', models.IntegerField(null=True, blank=True)),
                ('reading_present', models.IntegerField(null=True, blank=True)),
                ('reading_good', models.IntegerField(null=True, blank=True)),
                ('reading_fun', models.IntegerField(null=True, blank=True)),
                ('reading_choice', models.IntegerField(null=True, blank=True)),
                ('gender', models.ForeignKey(blank=True, to='datacollector.Gender', null=True)),
                ('subject', models.ForeignKey(to='datacollector.Subject')),
            ],
        ),
    ]
