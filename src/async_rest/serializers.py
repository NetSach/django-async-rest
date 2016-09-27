# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = (
            'uuid',
            'status',
            'message',
            'resource_url',
            'context',
            'progress',
        )

        read_only_fields = (
            'uuid',
            'status',
            'message',
            'resource_url',
            'progress',
        )

    resource_url = serializers.SerializerMethodField()

    def get_resource_url(self, instance):
        if instance is None:
            return ''

        return ''.join([
            self.context.get('request').scheme,
            '://',
            self.context.get('request').get_host(),
            instance.resource_url,
        ])
