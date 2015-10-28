# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mountains', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mountain',
            name='address',
            field=models.CharField(max_length=255, default='1111 Somestreet Way, Somecity, AB 11111'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mountain',
            name='latitude',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mountain',
            name='longitude',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
