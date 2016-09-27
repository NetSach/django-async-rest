# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from django.dispatch import Signal


attrs = ['uuid', 'resource_name', 'action', 'context', 'resource_url', 'message']

queued = Signal(providing_args=attrs)
updated = Signal(providing_args=attrs)
completed = Signal(providing_args=attrs)
failed = Signal(providing_args=attrs)
