# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from rest_framework import status
from rest_framework import test
from rest_framework.reverse import reverse
from async_rest.models import Order
from async_rest.dispatcher import dispatcher
from async_rest.helpers import fail_on_error


class Handler(object):
    def __init__(self, testname):
        self.task_call_count = {}
        self.task_call_count[testname] = 0
        self.testname = testname

    def task(self, uuid, **kwargs):
        self.task_call_count[self.testname] += 1

    def failed_task(self, uuid, **kwargs):
        self.task_call_count[self.testname] += 1

    @property
    def count(self):
        return self.task_call_count[self.testname]


class BasicTestSuite(test.APITestCase):
    def setUp(self):
        dispatcher.use_taskqueue = False

    def test_order_french_fries(self):
        context = {'size': 'XL'}
        resource_name = 'french-fries'

        handler = Handler('test_order_french_fries')
        dispatcher.register('french-fries', handler.task, 'queued')

        # Place an order
        res = self.client.post(
            reverse('async-rest:place-order',
                    kwargs={'resource_name': resource_name}),
            {
                'context': context
            },
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)


        # Retrieve order and get status

        res = self.client.get(res.url)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        order = Order.objects.get(uuid=res.data['uuid'])

        # Test assertions
        self.assertEqual(res.data['status'], 'queued', msg=res.data['message'])
        self.assertEqual(res.data['context'], context)
        self.assertEqual(order.resource_name, resource_name)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)

        # Proceed with order - Out of band modifications
        order.status = 'running'
        order.message = 'cooking...'
        order.save()

        # Retrieve order and get status
        res = self.client.get(order.get_absolute_url())

        # Test assertions
        self.assertEqual(res.data['status'], 'running')
        self.assertEqual(res.data['message'], 'cooking...')
        self.assertEqual(res.data['context'], context)
        self.assertEqual(order.resource_name, resource_name)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)

        # Proceed with order - Out of band modifications
        order.status = 'completed'
        order.message = 'ready'
        order.resource_url = '/fries/bucket/2/'
        order.save()

        # Retrieve order and get status
        res = self.client.get(order.get_absolute_url())

        # Test assertions
        self.assertEqual(res.data['status'], 'completed')
        self.assertEqual(res.data['message'], 'ready')
        self.assertEqual(res.data['resource_url'], 'http://testserver/fries/bucket/2/')
        self.assertEqual(res.data['context'], context)
        self.assertEqual(order.resource_name, resource_name)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_dispatcher(self):
        context = {
            'size': 'XXL'
        }
        resource_name = 'french-fries'

        handler = Handler('test_dispatcher')
        dispatcher.register('french-fries', handler.task, 'queued')

        # Place an order
        res = self.client.post(
            reverse('async-rest:place-order', kwargs={'resource_name':resource_name}),
            {
                'context': context
            },
            format='json'
        )
        self.assertEqual(handler.count, 1)

    def test_invalid_values(self):
        resource_name = 'rotted-french-fries'
        handler = Handler('test_invalid_values')

        def made_to_fail(order_uuid, **kwargs):
            order = Order.objects.get(uuid=order_uuid)
            with fail_on_error(order, 'msg', status='failed'):

                raise Exception('I was made to fail')

        # Register invalid call back (logged through logging/error)
        dispatcher.register(resource_name, made_to_fail, 'queued')
        dispatcher.register(resource_name, handler.failed_task, 'failed')

        # Place an invalid order
        res = self.client.post(
            reverse('async-rest:place-order', kwargs={'resource_name':resource_name}),
            {
                'context': {}
            },
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        # Retrieve order and get status

        res = self.client.get(res.url)
        # Test assertions
        self.assertEqual(res.data['status'], 'failed')
        self.assertEqual(handler.count, 1)

        # Place another invalid order
        res = self.client.post(
            reverse('async-rest:place-order', kwargs={'resource_name':resource_name}),
            {
                'context': '"size": "XL"'
            },
            format='json'
        )
        # Retrieve error
        context = res.data.get('context')
        self.assertIsNotNone(context)
        self.assertTrue(context[0].endswith('is not a valid JSON string.'))


    def test_actions(self):
        """
        Test multiple actions on order
        """
        resource_name = 'multiple-actions'
        handler_create = Handler('test_creation')
        handler_destroy = Handler('test_deletion')

        # Register 2 tasks on same resource
        # but with different actions
        dispatcher.register_create(resource_name, handler_create.task)
        dispatcher.register_destroy(resource_name, handler_destroy.task)

        # Common url
        url = reverse('async-rest:place-order', kwargs={'resource_name':resource_name})

        # No actions yet
        self.assertEqual(handler_create.count, 0)
        self.assertEqual(handler_destroy.count, 0)

        # Place a creation order
        res = self.client.post(
            url,
            {
                'context': {}
            },
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        # Retrieve order and get status

        res = self.client.get(res.url)

        # Check response
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(res.data['status'], 'queued')

        # One creation, no deletion yet
        self.assertEqual(handler_create.count, 1)
        self.assertEqual(handler_destroy.count, 0)

        # Place a deletion order
        res = self.client.delete(
            url,
            {
                'context': {}
            },
            format='json'
        )

        # Retrieve order and get status
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

        res = self.client.get(res.url)

        # Check response
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(res.data['status'], 'queued')

        # One creation, One deletion
        self.assertEqual(handler_create.count, 1)
        self.assertEqual(handler_destroy.count, 1)

    def tearDown(self):
        pass
