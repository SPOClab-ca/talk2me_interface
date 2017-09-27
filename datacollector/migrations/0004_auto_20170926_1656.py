# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datacollector', '0003_session_response_num_repeats'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject_UsabilitySurvey_Type',
            fields=[
                ('usabilitysurvey_type_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='subject_usabilitysurvey',
            name='usabilitysurvey_type_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
