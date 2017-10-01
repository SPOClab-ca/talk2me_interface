# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datacollector', '0004_auto_20170926_1656'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject_Gender',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='gender',
            name='requires_detail',
            field=models.IntegerField(default=0),
        ),
    ]
