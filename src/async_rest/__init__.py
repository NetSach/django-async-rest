# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function


default_app_config = 'async_rest.apps.Config'
VERSION = (1, 0, 0)


def get_version(version=None):
    return '.'.join(map(str, VERSION))


__version__ = get_version(VERSION)
