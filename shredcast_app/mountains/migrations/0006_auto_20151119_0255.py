# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mountains', '0005_snowreport_snow_next_week'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherReport',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('date_time', models.DateTimeField()),
                ('today_temp_low', models.IntegerField()),
                ('today_temp_high', models.IntegerField()),
                ('today_weather', models.CharField(max_length=100)),
                ('today_wind', models.IntegerField()),
                ('tomorrow_temp_low', models.IntegerField()),
                ('tomorrow_temp_high', models.IntegerField()),
                ('tomorrow_weather', models.CharField(max_length=100)),
                ('tomorrow_wind', models.IntegerField()),
                ('mountain', models.ForeignKey(to='mountains.Mountain')),
            ],
        ),
        migrations.RenameField(
            model_name='snowreport',
            old_name='datetime',
            new_name='date_time',
        ),
    ]
