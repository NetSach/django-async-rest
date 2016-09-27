# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from django.conf.urls import url, patterns
from .views import (
    PlaceOrder,
    OrderView,
)


urlpatterns = patterns(
    '',
    url(r'^(?P<resource_name>[^/]+)/order/$', PlaceOrder.as_view(),
        name='place-order'),
    url(r'^orders/(?P<uuid>[^/]+)/$', OrderView.as_view(),
        name='order-detail'),
)
