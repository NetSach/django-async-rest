# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import transaction
from django.shortcuts import redirect
from rest_framework import status
from rest_framework import response
from rest_framework import generics
from ..serializers import OrderSerializer
from ..models import Order
import logging

logger = logging.getLogger()


class PlaceOrder(generics.CreateAPIView, generics.DestroyAPIView):
    model = Order
    serializer_class = OrderSerializer

    def build_order(self, request, action, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            self.perform_create(serializer)
            serializer.instance.resource_name = kwargs.get('resource_name')
            serializer.instance.action = action
            serializer.instance.save()

        with transaction.atomic():
            order_uuid = serializer.instance.uuid
            order = Order.objects.get(uuid=order_uuid)

        order.queue()

        return redirect(order)

    def post(self, request, *args, **kwargs):
        return self.build_order(request, 'create', *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.build_order(request, 'update', *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.build_order(request, 'destroy', *args, **kwargs)


class OrderView(generics.RetrieveAPIView):
    model = Order
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    lookup_field = 'uuid'

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order)
        status_code = status.HTTP_200_OK

        if order.status in ['queued', 'running']:
            status_code = status.HTTP_202_ACCEPTED

        elif order.status == 'completed' and order.action == 'create':
            status_code = status.HTTP_201_CREATED

        return response.Response(serializer.data, status=status_code)
