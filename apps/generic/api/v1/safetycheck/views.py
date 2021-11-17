from copy import copy
from collections import Counter

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import F
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.db.models.expressions import Exists, OuterRef
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from rest_framework import viewsets, status as response_status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from .serializers import CreateSafetyCheckSerializer, ListSafetyCheckSerializer, RetrieveSafetyCheckSerializer, UpdateSafetyCheckSerializer
from ....permissions import IsActivityAuthorOrReadOnly

Activity = apps.get_registered_model('generic', 'Activity')
SafetyCheck = apps.get_registered_model('generic', 'SafetyCheck')


class BaseViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.context = dict()

    def initialize_request(self, request, *args, **kwargs):
        self.context.update({'request': request})
        return super().initialize_request(request, *args, **kwargs)


class SafetyCheckAPIViewSet(BaseViewSet):
    """
    GET
    -----

        {
            "content_type": "hazard",
            "object_id": "8364b649-ede9-4d8a-9128-1984a857cb43",
            "condition": "affected",
            "user": "hexid"
        }


    POST
    -----

        {
            "content_type": "hazard",
            "object_id": "8364b649-ede9-4d8a-9128-1984a857cb43",
            "condition": "affected",
            "situation": "sangat dalam",
            "attachments": [
                "f75ea312-45ab-4028-932f-d0aea09d82f8"
            ],
            "locations": [
                {
                    "latitude": 13.45151,
                    "longitude": -123.2522,
                    "impacts": [
                        {
                            "identifier": "102",
                            "value": "102",
                            "metric": "104",
                            "description": "Lorem ipsum dolor..."
                        }
                    ]
                }
            ]
        }
    """
    lookup_field = 'uuid'
    permissions_classes = (IsAuthenticated,)

    permission_action = {
        'list': (AllowAny,),
        'retrieve': (AllowAny,),
        'partial_update': (IsActivityAuthorOrReadOnly,),
        'destroy': (IsActivityAuthorOrReadOnly,),
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
            .filter(content_type__model=SafetyCheck._meta.model_name, object_id=OuterRef('id'))

        queryset = SafetyCheck.objects \
            .prefetch_related('user', 'content_type', 'locations', 'locations__impacts', 'attachments',
                              'content_object', 'content_object__user') \
            .select_related('user', 'content_type') \
            .annotate(authored=Exists(activity.filter(user_id=self.request.user.id))) \
            .order_by('-create_at')

        return queryset

    def get_filtered_queryset(self):
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        condition = self.request.query_params.get('condition')
        user_id = self.request.query_params.get('user_id')

        queryset = self.get_queryset()

        if condition:
            queryset = queryset.filter(condition=condition)

        # by user
        if user_id:
            queryset = queryset.filter(activities__user__hexid=user_id)

        if not content_type:
            raise ValidationError(detail=_("content_type required"))

        queryset = queryset.filter(content_type__model=content_type)

        if object_id:
            ct_param = dict()
            ct_objs = ContentType.objects.filter(model=content_type)

            for y in ct_objs:
                model = y.model_class()
                if model and hasattr(model, 'safetychecks'):
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
            queryset = queryset.filter(object_id=content_object.id)

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
        queryset = self.get_filtered_queryset()
        paginator = LimitOffsetPagination()
        paginate_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ListSafetyCheckSerializer(
            paginate_queryset,
            context=self.context,
            many=True
        )

        return paginator.get_paginated_response(serializer.data)

    @transaction.atomic
    def create(self, request):
        serializer = CreateSafetyCheckSerializer(
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
        serializer = RetrieveSafetyCheckSerializer(
            instance=instance,
            context=self.context
        )

        return Response(serializer.data, status=response_status.HTTP_200_OK)

    @transaction.atomic
    def partial_update(self, request, uuid=None):
        instance = self.get_object(uuid=uuid, for_update=True)
        self.check_object_permissions(request, instance)

        serializer = UpdateSafetyCheckSerializer(
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
        serializer = RetrieveSafetyCheckSerializer(
            instance_copy,
            context=self.context
        )

        return Response(serializer.data, status=response_status.HTTP_200_OK)

    """
    ACTION DECORATOR
    """
    @action(
        detail=False,
        methods=['get'],
        url_name='coordinate',
        permission_classes=(AllowAny,)
    )
    def coordinates(self, request):
        """
        GET
        -----
            Show only 30 days later

            {
                "startdate": "26-07-1989",
                "content_type": "hazard",
                "object_id": "8364b649-ede9-4d8a-9128-1984a857cb43"
            }
        """
        startdate = self.request.query_params.get('startdate')
        queryset = self.get_filtered_queryset()
        date_range = timezone.datetime.today() + timezone.timedelta(days=30)

        if startdate:
            startdate_dt = timezone.datetime.strptime(startdate, '%d-%m-%Y')
            date_range = startdate_dt + timezone.timedelta(days=30)

        queryset = queryset.filter(create_at__lte=date_range).values(
            'id',
            'condition',
            'situation',
            activity_author=F('activities__user__first_name'),
            latitude=F('locations__latitude'),
            longitude=F('locations__longitude'),
        )

        latitudes = [round(x.get('latitude'), 2) for x in queryset]
        latitudes_intensity = Counter(latitudes)

        longitudes = [round(x.get('longitude'), 2) for x in queryset]
        longitudes_intensity = Counter(longitudes)

        coordinates_intensity = list()
        longitudes_intensity_keys = list(longitudes_intensity.keys())

        for index, value in enumerate(latitudes_intensity.items()):
            lat = value[0]
            lng = longitudes_intensity_keys[index]
            intensity = value[1]
            coord = [lat, lng, intensity]
            coordinates_intensity.append(coord)

        response = {
            'list': queryset,
            'intensity': coordinates_intensity
        }
        return Response(response, status=response_status.HTTP_200_OK)
