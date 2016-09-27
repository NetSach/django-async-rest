# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function


ACTIONS = (
    ('create', 'Create a resource'),
    ('update', 'Update a resource'),
    ('destroy', 'Destroy a resource'),
)

STATES = (
    ('queued', 'queued'),
    ('running', 'running'),
    ('completed', 'completed'),
    ('failed', 'failed'),
)
