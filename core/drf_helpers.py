from collections import OrderedDict

from rest_framework import serializers
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.utils.urls import remove_query_param, replace_query_param
from rest_framework.response import Response


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class GeneralModelSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = None
        fields = '__all__'


class LimitOffsetPaginationExtend(LimitOffsetPagination):
    def get_last_link(self):
        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        offset = self.count - self.limit
        return replace_query_param(url, self.offset_query_param, offset)

    def get_first_link(self):
        url = self.request.build_absolute_uri()
        return remove_query_param(url, self.offset_query_param)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('first', self.get_first_link()),
            ('last', self.get_last_link()),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
