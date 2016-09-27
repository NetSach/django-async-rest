# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from async_rest.models import Order
from async_rest.helpers import ProgressItems
from rest_framework import test


class ProgressTestSuite(test.APITestCase):
    def setUp(self):
        pass

    def test_progress(self):
        """
        Test the Progress helper
        """
        order = Order.objects.create()
        self.assertEqual(order.progress, 0.0)

        check = 0
        with ProgressItems(order, range(10)) as items:
            for item in items:
                self.assertEqual(item, check)
                self.assertEqual(Order.objects.first().progress, check*10.0)
                check += 1

    def test_progress_iterator(self):
        """
        Test the Progress helper
        using an iterator
        """
        length = 1000
        order = Order.objects.create()
        self.assertEqual(order.progress, 0.0)

        check = 0
        with ProgressItems(order, xrange(length), length=length) as items:
            for item in items:
                self.assertEqual(item, check)
                self.assertAlmostEqual(Order.objects.first().progress, check*0.1)
                check += 1
