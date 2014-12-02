# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=50, null=True, blank=True)),
                ('serial_no', models.CharField(max_length=50)),
                ('counter', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('purpose', models.CharField(max_length=25, choices=[(b'SLC', b'Scilab Conference'), (b'SPC', b'Scipy Conference'), (b'PTC', b'Python Textbook Companion'), (b'STC', b'Scilab Textbook Companion')])),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uin', models.CharField(max_length=50)),
                ('attendance', models.NullBooleanField()),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scilab_import',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('ticket_number', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('email', models.CharField(max_length=50, null=True, blank=True)),
                ('ticket', models.CharField(max_length=50, null=True, blank=True)),
                ('date', models.CharField(max_length=50, null=True, blank=True)),
                ('order_id', models.IntegerField(default=0, null=True, blank=True)),
                ('purpose', models.CharField(default=b'SLC', max_length=10)),
            ],
            options={
                'managed': True,
            },
            bases=(models.Model,),
        ),
    ]
