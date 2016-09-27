# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig


class Config(AppConfig):
    name = 'async_rest'
    verbose_name = _('Async REST')

