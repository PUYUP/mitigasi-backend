from copy import copy

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.apps import apps
from django.db.models import Q, F
from django.db.models.aggregates import Count
from django.db.models.expressions import Case, Exists, OuterRef, Value, When
from django.db.models.fields import BooleanField
from django.utils import timezone

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import CreateHazardSerializer, ListHazardSerializer, RetrieveHazardSerializer, UpdateHazardSerializer
from ....permissions import IsHazardAuthorOrReadOnly
from ....models import DISASTER_CLASSIFY_MODEL_MAPPER

Hazard = apps.get_registered_model('threat', 'Hazard')
SafetyCheck = apps.get_registered_model('generic', 'SafetyCheck')


class BaseViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.context = dict()

    def initialize_request(self, request, *args, **kwargs):
        self.context.update({'request': request})
        return super().initialize_request(request, *args, **kwargs)


class HazardAPIViewSet(BaseViewSet):
    """
    GET
    -----

        {
            "classify": "101",
            "user": "hexid"
        }


    POST
    -----

        `classify` default as 999 (other) (optional)
        `incident` name of hazard (required)
        `occur_at` valid UTC time format (required)
        `attachments` if attachment has `hazard` before, after saved replace `attachments` uuid
        with new attachment uuid

        {
            "classify": "101",
            "incident": "banjir bro",
            "description": "lipsum",
            "occur_at": "2012-09-04 06:00:00.000000",
            "source": "BMKG",
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


    PATCH
    -----

        {
            "classify": "101",
            "incident": "banjir bro",
            "description": "lipsum",
            "occur_at": "2012-09-04 06:00:00.000000",
            "attachments": [
                "f75ea312-45ab-4028-932f-d0aea09d82f8"
            ],
            "locations": [
                {
                    "uuid": "uuid4", // for update or delete
                    "delete": boolean, // mark as delete
                    "latitude": 13.45151,
                    "longitude": -123.2522,
                    "impacts": [
                        {
                            "uuid": "uuid4", // for update or delete
                            "delete": boolean, // mark as delete
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
    permission_classes = (IsAuthenticated,)

    permission_action = {
        'list': (AllowAny,),
        'retrieve': (AllowAny,),
        'partial_update': (IsHazardAuthorOrReadOnly,),
        'destroy': (IsHazardAuthorOrReadOnly,),
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
        safetychecks = SafetyCheck.objects \
            .filter(object_id=OuterRef('id'), content_type__model=Hazard._meta.model_name)

        disaster_related = list()
        for classify, model in DISASTER_CLASSIFY_MODEL_MAPPER.items():
            disaster_related.append(model._meta.model_name)

        queryset = Hazard.objects \
            .prefetch_related('locations', 'locations__impacts', 'attachments',
                              'activities', 'activities__user', *disaster_related) \
            .select_related(*disaster_related) \
            .annotate(
                authored=Case(
                    When(
                        activities__isnull=True,
                        then=Value(False)
                    ),
                    When(
                        activities__user_id=self.request.user.id,
                        then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                comment_count=Count('comments', distinct=True),
                safetycheck_affected_count=Count(
                    'safetychecks',
                    filter=Q(safetychecks__condition='affected'),
                    distinct=True
                ),
                safetycheck_safe_count=Count(
                    'safetychecks',
                    filter=Q(safetychecks__condition='safe'),
                    distinct=True
                ),
                safetycheck_confirmed=Exists(
                    safetychecks.filter(
                        activities__user_id=self.request.user.id
                    )
                )
            ) \
            .order_by('-create_at')

        return queryset

    def get_filtered_queryset(self):
        classify = self.request.query_params.get('classify')
        user = self.request.query_params.get('user')

        queryset = self.get_queryset()

        # by classify
        if classify:
            try:
                model_name = DISASTER_CLASSIFY_MODEL_MAPPER[classify]._meta.model_name
            except IndexError:
                model_name = None

            if model_name:
                queryset = queryset.filter(
                    **{'%s__isnull' % model_name: False}
                )

        # by user
        if user:
            queryset = queryset.filter(activities__user__hexid=user)

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
        serializer = ListHazardSerializer(
            paginate_queryset,
            context=self.context,
            many=True
        )

        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, uuid=None):
        instance = self.get_object(uuid=uuid)
        serializer = RetrieveHazardSerializer(
            instance=instance,
            context=self.context
        )

        return Response(serializer.data, status=response_status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request):
        serializer = CreateHazardSerializer(
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

    @transaction.atomic
    def partial_update(self, request, uuid=None):
        instance = self.get_object(uuid=uuid, for_update=True)
        self.check_object_permissions(request, instance)

        serializer = UpdateHazardSerializer(
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
        serializer = RetrieveHazardSerializer(
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
                "classify": "108",
                "startdate": "26-07-1989"
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
            'classify',
            'incident',
            'description',
            latitude=F('locations__latitude'),
            longitude=F('locations__longitude'),
        )

        return Response(queryset, status=response_status.HTTP_200_OK)
