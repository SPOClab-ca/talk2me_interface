# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datacollector', '0002_auto_20170410_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='session_response',
            name='num_repeats',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
