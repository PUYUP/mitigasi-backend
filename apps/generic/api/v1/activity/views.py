from copy import copy

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.apps import apps
from django.db.models.expressions import Case, Value, When
from django.db.models.fields import BooleanField

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from apps.threat.models import DISASTER_CLASSIFY_MODEL_MAPPER

from .serializers import ListActivitySerializer, RetrieveActivitySerializer, UpdateActivitySerializer
from ....permissions import IsActivityAuthorOrReadOnly

Activity = apps.get_registered_model('generic', 'Activity')


class BaseViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.context = dict()

    def initialize_request(self, request, *args, **kwargs):
        self.context.update({'request': request})
        return super().initialize_request(request, *args, **kwargs)


class ActivityAPIViewSet(BaseViewSet):
    """
    GET
    -----

        {
            "content_type": "hazard"
        }
    """
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    permission_action = {
        'list': (AllowAny,),
        'retrieve': (AllowAny,),
        'destroy': (IsActivityAuthorOrReadOnly,),
        'partial_update': (IsActivityAuthorOrReadOnly,),
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
        content_object_prefetch = list()
        for classify, model in DISASTER_CLASSIFY_MODEL_MAPPER.items():
            model_name = model._meta.model_name
            prefetch = 'content_object__%s' % model_name
            content_object_prefetch.append(prefetch)

        queryset = Activity.objects \
            .prefetch_related('content_type', 'content_object', 'user', *content_object_prefetch) \
            .select_related('content_type', 'user') \
            .annotate(
                authored=Case(
                    When(
                        user_id=self.request.user.id,
                        then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField()
                )
            ) \
            .order_by('-create_at')

        return queryset

    def get_object(self, uuid, for_update=False):
        queryset = self.get_queryset()

        try:
            if for_update:
                instance = queryset.select_for_update().get(uuid=uuid)
            else:
                instance = queryset.get(uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound

        return instance

    def list(self, request):
        content_type = request.query_params.get('content_type')
        queryset = self.get_queryset()

        if content_type:
            queryset = queryset.filter(content_type__model=content_type)

        paginator = LimitOffsetPagination()
        paginate_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ListActivitySerializer(
            paginate_queryset,
            context=self.context,
            many=True
        )

        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, uuid=None):
        instance = self.get_object(uuid=uuid)
        serializer = RetrieveActivitySerializer(
            instance=instance,
            context=self.context
        )

        return Response(serializer.data, status=response_status.HTTP_200_OK)

    @transaction.atomic
    def partial_update(self, request, uuid=None):
        instance = self.get_object(uuid=uuid, for_update=True)
        self.check_object_permissions(request, instance)

        serializer = UpdateActivitySerializer(
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
        serializer = RetrieveActivitySerializer(
            instance_copy,
            context=self.context
        )

        return Response(serializer.data, status=response_status.HTTP_200_OK)
