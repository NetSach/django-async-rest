# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from django.utils.translation import ugettext_lazy as _
import uuid
from django.db import models
from jsonfield import JSONField
import logging
from rest_framework.reverse import reverse
from .validators import validate_json
from .signals import (
    updated,
    queued,
    failed
)
from .constants import (
    ACTIONS,
    STATES,
)


class AbstractOrder(models.Model):
    class Meta:
        abstract = True

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    status = models.CharField(max_length=32, choices=STATES, default='queued')

    resource_url = models.URLField(max_length=1024, default='')

    message = models.TextField(default='')

    context = JSONField(blank=True, validators=[validate_json])

    resource_name = models.CharField(max_length=200)

    action = models.CharField(max_length=32, choices=ACTIONS, default='create')

    queue_name = models.CharField(max_length=150, blank=True)

    created = models.DateTimeField(
        verbose_name=_('Created'),
        auto_now_add=True,
    )

    updated = models.DateTimeField(
        verbose_name=_('Updated'),
        auto_now=True,
    )

    progress = models.FloatField(default=0.0, null=True, blank=True)

    def get_absolute_url(self, request=None):
        return reverse(
            'async-rest:order-detail',
            args=[self.uuid],
            request=request,
        )

    def queue(self):
        """
        Queue order in task list
        """
        res = queued.send_robust(
            self.__class__,
            uuid=self.uuid,
            status=self.status,
            resource_url=self.resource_url,
            message=self.message,
            context=self.context,
            action=self.action,
            resource_name=self.resource_name,
        )
        return res

    def fail(self):
        res = failed.send_robust(
            self.__class__,
            uuid=self.uuid,
            status=self.status,
            message=self.message,
            resource_name=self.resource_name,
            context=self.context,
            resource_url=self.resource_url,
            progress=self.progress,
        )
        return res

    def save(self, *args, **kwargs):
        updated.send_robust(
            self.__class__,
            uuid=self.uuid,
            status=self.status,
            message=self.message,
            resource_name=self.resource_name,
            context=self.context,
            resource_url=self.resource_url,
            progress=self.progress,
        )

        return super(AbstractOrder, self).save(*args, **kwargs)

    def update_progress(self, percent):
        """
        Low level method to update progress
        """
        if percent >= 100.0:
            percent = 100.0

        if percent <= 0.0:
            percent = 0.0

        self.progress = percent
        self.save()

    def __unicode__(self):
        return '{} <{}:{}>'.format(self._meta.object_name, self.uuid, self.status)


class Order(AbstractOrder):
    pass
