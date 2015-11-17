# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mountains', '0004_snowreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='snowreport',
            name='snow_next_week',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
