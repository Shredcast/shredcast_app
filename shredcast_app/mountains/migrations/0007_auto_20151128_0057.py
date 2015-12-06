# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mountains', '0006_auto_20151119_0255'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrailReport',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date_time', models.DateTimeField()),
                ('max_trails', models.PositiveIntegerField()),
                ('max_miles', models.PositiveIntegerField()),
                ('max_acres', models.PositiveIntegerField()),
                ('max_lifts', models.PositiveIntegerField()),
                ('open_trails', models.PositiveIntegerField()),
                ('open_miles', models.PositiveIntegerField()),
                ('open_acres', models.PositiveIntegerField()),
                ('open_lifts', models.PositiveIntegerField()),
                ('parks_open', models.PositiveIntegerField()),
                ('park_features', models.PositiveIntegerField()),
                ('trail_map_small', models.CharField(max_length=256)),
                ('trail_map_large', models.CharField(max_length=256)),
                ('mountain', models.ForeignKey(to='mountains.Mountain')),
            ],
        ),
        migrations.AddField(
            model_name='snowreport',
            name='primary_condition',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='weatherreport',
            name='today_base_temp',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='weatherreport',
            name='today_summit_temp',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
