# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OwnerModel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('owner_id', models.IntegerField(default=-1)),
                ('plugin_id', models.IntegerField(default=-1)),
                ('token', models.CharField(max_length=200)),
                ('url', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ParticipantModel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('instance_id', models.IntegerField(default=-1)),
                ('phone_number', models.CharField(max_length=30)),
                ('owner_id', models.IntegerField(default=-1)),
            ],
        ),
    ]
