# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from collections import defaultdict
from .models import ACTIONS
from .signals import (
    queued,
    updated,
    completed,
    failed,
)


class OrderDispatcher(object):
    """
    use_taskqueue : call task using .apply_async(args, kwargs)
    """
    def __init__(self, use_taskqueue=False):
        self.use_taskqueue = use_taskqueue
        self._handlers = defaultdict(dict)

    def register(self, resource_name, task, signame='queued', action='create',
                 queue_name=None):
        if action not in dict(ACTIONS):
            raise Exception('Unsupported action: {}'.format(action))

        if resource_name not in self._handlers[signame]:
            self._handlers[signame][resource_name] = {}

        if action not in self._handlers[signame][resource_name]:
            self._handlers[signame][resource_name][action] = []

        self._handlers[signame][resource_name][action].append((task, queue_name))

    def register_create(self, *args, **kwargs):
        return self.register(action='create', *args, **kwargs)

    def register_update(self, *args, **kwargs):
        return self.register(action='update', *args, **kwargs)

    def register_destroy(self, *args, **kwargs):
        return self.register(action='destroy', *args, **kwargs)

    def _call_tasks(self, signame, **kwargs):
        resource_name = kwargs.get('resource_name')
        context = kwargs.get('context') or {}
        uuid = kwargs.get('uuid')
        action = kwargs.get('action', 'create')

        if signame not in self._handlers:
            return

        if resource_name not in self._handlers[signame]:
            return

        if action not in self._handlers[signame][resource_name]:
            return

        task_list = self._handlers[signame][resource_name][action]

        for task, queue_name in task_list:
            if self.use_taskqueue:
                delayed_func = getattr(task, 'apply_async', None)
                if delayed_func is None:
                    raise RuntimeError(
                        'Task {} does not support .apply_async'.format(
                            repr(task))
                    )
                else:
                    if queue_name is not None:
                        task.apply_async(args=[uuid], kwargs=context, queue=queue_name)
                    else:
                        task.apply_async(args=[uuid], kwargs=context)
            else:
                task(uuid, **context)

    def process_queued(self, sender, **kwargs):
        self._call_tasks('queued', **kwargs)

    def process_updated(self, sender, **kwargs):
        self._call_tasks('updated', **kwargs)

    def process_completed(self, sender, **kwargs):
        self._call_tasks('completed', **kwargs)

    def process_failed(self, sender, **kwargs):
        self._call_tasks('failed', **kwargs)


dispatcher = OrderDispatcher()

queued.connect(dispatcher.process_queued)
updated.connect(dispatcher.process_updated)
completed.connect(dispatcher.process_completed)
failed.connect(dispatcher.process_failed)
