******************************
Asynchronous RESTFul Interface
******************************

Introduction
============

This application provides a standardized way of creating asynchronous RESTful APIs.
The main goal is to never block a client performing a request by offloading a
long running process using a task queue, or similar mechanisms.

This application does not restrict usage of a specific task manager and a dummy
queue is available to perform tests.


Installation
============

To install the application in a django project, proceed as described hereunder:

- Add 'async_rest.async_rest' to settings.INSTALLED_APPS


.. code-block:: python

    INSTALLED_APPS = [
        ...
        'async_rest.async_rest',
        ...
    ]


- Add urls :

.. code-block:: python

    urlpatterns = patterns(
        '',
        ...
        (r'^api/async/', include('async_rest.async_rest.urls', namespace='async_rest')),
        ...
    )


Target workflow
===============

Workflow without notifications
------------------------------

The target workflow is the following:

.. code-block:: text

    # The client orders a resource from the server that will take some time
    # (e.g. "Create and provision a virtual machine" )

    [client] ---  (1) order-resource  --> [server/resource/order] (method=POST)
                      context = {...}

    # The server answers back with a receipt containing an url where
    # the client can obtain more information about the completion of its order

    [client] <--  (1) receipt  --- [server/resource/order] (status=202)
                      order-url = xxx

    # At any time, the client can obtain information about its order

    [client] ---  (2) order-status   --> [server/xxx] (method=GET)
    [client] <--  (2) order-status   --- [server/xxx] (status=200)
                      order-uid = nnn
                      status = yyy
                      resource-url = null
                      context = {...}

    # Upon completion of the request, the server will provide a resource url
    # in the response of the order-status request

    [client] ---  (3) order-status   --> [server/xxx] (method=GET)
    [client] <--  (3) order-status   --- [server/xxx] (status=200)
                      order-uid = nnn
                      status = completed
                      resource-url = zzz
                      context = {...}

    # The client is able to retrieve the required resource

    [client] ---  (4) resource   --> [server/zzz] (method=GET)
    [client] <--  (4) resource   --- [server/zzz] (status=200)



Data model
==========

.. _order-model:

**Order**

:uid: [client:read-only] Unique identifier
:status: [client:read-only] Status of the order among the values [``queued``, ``running``, ``completed``, ``failed``, ``aborted``]
:message: [client:read-only] Extended information provided in addition to the status
:resource-url: [client:read-only] Resource url, set upon completion of the order
:context: [client:read-write] Context to be passed to the handler in charge of actually creating the resource. This field can only be set upon creation of the order.

.. _receipt-model:

**Receipt**

:order-url: [client:read-only] Origin order url where the status can be obtained


Endpoints
=========

Order placement
---------------

.. http:post:: /api/v1.0/(str:resource-name)/order

    :synopsis: Place an order for *resource-name*
    :<json order: :ref:`Order <order-model>`
    :>json receipt: :ref:`Receipt <receipt-model>`
    :statuscode 202: The order is accepted and the work is offloaded to the task runner
    :statuscode 400: A problem with the request occurred, check the context

    Client request :

    .. sourcecode:: http

        POST /api/v1.0/french-fries/order HTTP/1.1

        {
            "context": {
                "size": "large"
            }
        }


    Server response :

    .. sourcecode:: http

        HTTP/1.1 202 Accepted

        {
            "order-url": "/api/v1.0/french-fries/order-status/46ee19a7-4216-47c9-831c-8745473a1545"
        }


Order status
------------

.. http:get:: /api/v1.0/(str:resource-name)/order-status/(str:order-uid)

    :synopsis: Obtain status of a specific order
    :>json order: :ref:`Order <order-model>`
    :statuscode 200: Order status returned
    :statuscode 404: The order was not found, check the receipt.

    Client request :

    .. sourcecode:: http

        GET /api/v1.0/french-fries/order-status/46ee19a7-4216-47c9-831c-8745473a1545 HTTP/1.1


    Server response :

    .. sourcecode:: http

        HTTP/1.1 200 OK

        {
            "status": "pending",
            "message": "cooking...",
            "resource-url": null,
            "context": {
                "size": "large"
            }
        }

    Server response upon completion :

    .. sourcecode:: http

        HTTP/1.1 200 OK

        {
            "status": "completed",
            "message": "served",
            "resource-url": "/api/v1.0/french-fries/dae2493414eb",
            "context": {
                "size": "large"
            }
        }


Usage
=====

- Create an asynchronous manager (e.g.: async_manager.py) that will handle the orders as they come and go:

.. code-block:: python

    from async_rest.async_rest.dispatcher import dispatcher

    # Set the following to True when you use celery tasks or when your task has
    # a .delay(*args, *kwargs) method.
    dispatcher.use_taskqueue = True

    dispatcher.register(<resource-name>, <task_fn>, 'order_queued')
    # dispatcher.register(<resource-name>, <task_fn>, 'order_completed')
    # dispatcher.register(<resource-name>, <task_fn>, 'order_failed')
    # dispatcher.register(<resource-name>, <task_fn>, 'order_changed')

Upon reception of an order, it will be queued and <task_fn> will be called. <task_fn> must have the following signature :

.. py:function:: task_name(uid, **context)

    Task to be called

    :param uuid uid: The order uid
    :param dict context: The context sent with the order


Exemple task :

.. code-block:: python

    ...
    from async_rest.async_rest.helpers import *
    from async_rest.async_rest.models import *

    @app.task()
    def task_cook_fries(uid, **kwargs):
        order = Order.objects.get(uid=order_uid)

        size = kwargs.get('size')

        with fault_intolerant(order, msg='Error message here'):
            # if cook_fries raises an exception, the order status will be 'failed'
            # and the error message will be set to order.message

            cook_fries(size)

            # In case of success, completes order
            order.status = 'completed'
            order.message = 'Fries ready'

    ...