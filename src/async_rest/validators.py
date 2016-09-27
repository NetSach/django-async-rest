# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from django.core.exceptions import ValidationError


def validate_json(value):
    if type(value) is not dict:
        raise ValidationError('{} is not a valid JSON string.'.format(value))
