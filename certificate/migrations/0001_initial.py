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
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.CharField(max_length=1000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CEP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_name', models.CharField(max_length=500)),
                ('student_name', models.CharField(max_length=200)),
                ('incharge', models.CharField(max_length=200)),
                ('coordinator', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=75)),
                ('institute', models.CharField(max_length=2000, null=True, blank=True)),
                ('purpose', models.CharField(default=b'CEP', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('email', models.CharField(max_length=300, null=True, blank=True)),
                ('serial_no', models.CharField(max_length=50)),
                ('counter', models.IntegerField()),
                ('workshop', models.CharField(max_length=1000, null=True, blank=True)),
                ('paper', models.CharField(max_length=1000, null=True, blank=True)),
                ('verified', models.IntegerField(default=0)),
                ('serial_key', models.CharField(max_length=200, null=True)),
                ('short_key', models.CharField(max_length=50, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('purpose', models.CharField(max_length=25)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedBack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('institution', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=50)),
                ('pin_number', models.CharField(max_length=10)),
                ('state', models.CharField(max_length=50)),
                ('purpose', models.CharField(default=b'SLC', max_length=10)),
                ('submitted', models.BooleanField(default=False)),
                ('answer', models.ManyToManyField(to='certificate.Answer')),
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
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=500)),
                ('purpose', models.CharField(default=b'SLC', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(to='certificate.Question'),
            preserve_default=True,
        ),
    ]
