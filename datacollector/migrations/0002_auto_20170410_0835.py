# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datacollector', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject_usabilitysurvey',
            name='response_id',
            field=models.TextField(null=True, blank=True),
        ),
    ]
