# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import uuid
import async_rest.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('status', models.CharField(default='queued', max_length=32, choices=[('queued', 'queued'), ('running', 'running'), ('completed', 'completed'), ('failed', 'failed')])),
                ('resource_url', models.URLField(default='', max_length=1024)),
                ('message', models.TextField(default='')),
                ('context', jsonfield.fields.JSONField(default=dict, blank=True, validators=[async_rest.validators.validate_json])),
                ('resource_name', models.CharField(max_length=200)),
                ('action', models.CharField(default='create', max_length=32, choices=[('create', 'Create a resource'), ('update', 'Update a resource'), ('destroy', 'Destroy a resource')])),
                ('queue_name', models.CharField(max_length=150, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated')),
                ('progress', models.FloatField(default=0.0, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
