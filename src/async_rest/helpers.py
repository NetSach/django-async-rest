# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
import StringIO
import traceback
import contextlib
import django.db
import logging


@contextlib.contextmanager
def fail_on_error(order, msg, status='failed'):
    """
    Context manager catching exception and failing automatically an order

    Logs error (traceback) using logging module and set ``message`` attribute
    of the order.
    """
    try:

        yield

    except Exception:
        msg_fp = StringIO.StringIO()
        traceback.print_exc(file=msg_fp)

        with django.db.transaction.atomic():
            order.message = '\n\nDetails:\n'.join([msg, msg_fp.getvalue()])
            order.status = status
            order.save()
            order.fail()

        message = 'Order {} failed.\n\n{}'.format(order.uuid, order.message)
        logging.error(message)
        raise RuntimeError(message)

    finally:
        order.save()


class ProgressItems(object):
    def __init__(self, order, items, length=None):
        self.order = order
        self.items = items
        if length and isinstance(length, int):
            self.length = length
        else:
            self.length = len(self.items)

    def __enter__(self):
        self.order.update_progress(0.0)

        for i, item in enumerate(self.items):
            yield item
            if self.length > 0:
                self.order.update_progress((i+1) * 100.0 / self.length)

    def __exit__(self, type, value, traceback):
        pass

