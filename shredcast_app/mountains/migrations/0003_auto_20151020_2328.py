# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mountains', '0002_auto_20151020_0126'),
    ]

    operations = [
        migrations.AddField(
            model_name='mountain',
            name='google_place_id',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='mountain',
            name='snocountry_id',
            field=models.CharField(default='', max_length=255),
        ),
    ]
