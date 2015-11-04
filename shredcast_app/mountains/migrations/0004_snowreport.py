# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mountains', '0003_auto_20151020_2328'),
    ]

    operations = [
        migrations.CreateModel(
            name='SnowReport',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('avg_base_depth_max', models.PositiveIntegerField()),
                ('snow_last_48', models.PositiveIntegerField()),
                ('snow_next_24', models.PositiveIntegerField()),
                ('snow_next_48', models.PositiveIntegerField()),
                ('snow_next_72', models.PositiveIntegerField()),
                ('mountain', models.ForeignKey(to='mountains.Mountain')),
            ],
        ),
    ]
