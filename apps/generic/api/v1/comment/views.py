from collections import OrderedDict
from copy import copy

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.db.models.aggregates import Count
from django.db.models.expressions import Exists, OuterRef
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.utils.urls import remove_query_param, replace_query_param

from .serializers import CreateCommentSerializer, ListCommentSerializer, RetrieveCommentSerializer, UpdateCommentSerializer
from ....permissions import IsCommentAuthorOrReadOnly

Activity = apps.get_registered_model('generic', 'Activity')
Comment = apps.get_registered_model('generic', 'Comment')


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


class BaseViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.context = dict()

    def initialize_request(self, request, *args, **kwargs):
        self.context.update({'request': request})
        return super().initialize_request(request, *args, **kwargs)


class CommentAPIViewSet(BaseViewSet):
    """
    GET
    -----

        {
            "content_type": "hazard",
            "object_id": "8364b649-ede9-4d8a-9128-1984a857cb43"
        }


    POST
    -----

        {
            "description": "Komentar",
            "content_type": "hazard",
            "object_id": "8364b649-ede9-4d8a-9128-1984a857cb43"
        }
    """
    lookup_field = 'uuid'
    permissions_classes = (IsAuthenticated,)

    permission_action = {
        'list': (AllowAny,),
        'retrieve': (AllowAny,),
        'partial_update': (IsCommentAuthorOrReadOnly,),
        'destroy': (IsCommentAuthorOrReadOnly,),
    }

    def get_permissions(self):
        """
        Instantiates and returns
        the list of permissions that this view requires.
        """
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        activity = Activity.objects \
            .filter(content_type__model='comment', object_id=OuterRef('id'))

        queryset = Comment.objects \
            .prefetch_related('user', 'child', 'child__parent', 'child__parent__user',
                              'content_object', 'content_object__comments') \
            .select_related('user', 'child', 'child__parent', 'child__parent__user') \
            .annotate(
                authored=Exists(activity.filter(user_id=self.request.user.id)),
                reply_count=Count('parents__child')
            ) \
            .order_by('create_at') \
            .reverse()

        return queryset

    def get_object(self, uuid, for_update=False):
        queryset = self.get_queryset()

        try:
            if for_update:
                instance = queryset.select_for_update().get(uuid=uuid)
            else:
                instance = queryset.get(uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound()

        return instance

    def list(self, request):
        content_type = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')
        queryset = self.get_queryset()

        if not content_type or not object_id:
            raise ValidationError(
                detail=_("content_type and object_id required"))

        ct_param = dict()
        ct_objs = ContentType.objects.filter(model=content_type)

        for y in ct_objs:
            model = y.model_class()
            if model and hasattr(model, 'comments'):
                ct_param.update({
                    'model': model._meta.model_name,
                    'app_label': model._meta.app_label,
                })

                break

        try:
            ct_obj = ContentType.objects.get(**ct_param)
        except ObjectDoesNotExist as e:
            raise NotFound(detail=str(e))

        content_object = ct_obj.get_object_for_this_type(uuid=object_id)
        queryset = queryset.filter(
            content_type__model=content_type,
            object_id=content_object.id
        )

        paginator = LimitOffsetPaginationExtend()
        paginate_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ListCommentSerializer(
            paginate_queryset,
            context=self.context,
            many=True
        )

        return paginator.get_paginated_response(reversed(serializer.data))

    @transaction.atomic
    def create(self, request):
        serializer = CreateCommentSerializer(
            data=request.data,
            context=self.context
        )

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except DjangoValidationError as e:
                raise ValidationError(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)

    def retrieve(self, request, uuid=None):
        instance = self.get_object(uuid=uuid)
        serializer = RetrieveCommentSerializer(
            instance=instance,
            context=self.context
        )

        return Response(serializer.data, status=response_status.HTTP_200_OK)

    @transaction.atomic
    def partial_update(self, request, uuid=None):
        instance = self.get_object(uuid=uuid, for_update=True)
        self.check_object_permissions(request, instance)

        serializer = UpdateCommentSerializer(
            instance=instance,
            data=request.data,
            partial=True,
            context=self.context
        )

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except DjangoValidationError as e:
                raise ValidationError(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)

    @transaction.atomic
    def destroy(self, request, uuid=None):
        instance = self.get_object(uuid=uuid, for_update=True)
        self.check_object_permissions(request, instance)

        # copy for response
        instance_copy = copy(instance)

        # run delete
        instance.delete()

        # return object
        serializer = RetrieveCommentSerializer(
            instance_copy,
            context=self.context
        )

        return Response(serializer.data, status=response_status.HTTP_200_OK)
