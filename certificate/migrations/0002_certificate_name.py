# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('certificate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate',
            name='name',
            field=models.CharField(default='ABC', max_length=100),
            preserve_default=False,
        ),
    ]
