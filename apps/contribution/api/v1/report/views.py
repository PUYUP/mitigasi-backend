from copy import copy

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Count
from django.db.models.expressions import Case, Value, When
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, status as response_status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import NotFound, ValidationError

from core.loading import build_pagination
from apps.contribution.mixins.permissions import IsActivityCreatorOrReadOnly

from .serializers import CreateReportSerializer, ListReportSerializer, RetrieveReportSerializer, UpdateReportSerializer

Report = apps.get_registered_model('contribution', 'Report')


class BaseViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.context = dict()

    def initialize_request(self, request, *args, **kwargs):
        self.context.update({'request': request})
        return super().initialize_request(request, *args, **kwargs)


class ReportAPIViewSet(BaseViewSet):
    """
    POST
    -----

        {
            "title": "Test laporan bencana",
            "occur_at": "2012-09-04 06:00:00.000000",
            "identifier": "101",
            "location": {
                "latitude": 1.24,
                "longitude": 0.25
            }
        }


    GET
    -----

        {
            "identifier": "101"
        }
    """
    lookup_field = 'uuid'
    throttle_classes = (AnonRateThrottle, UserRateThrottle,)
    permission_classes = (IsAuthenticated,)
    permission_action = {
        'list': (AllowAny,),
        'retrieve': (AllowAny,),
        'partial_update': (IsActivityCreatorOrReadOnly,),
        'destroy': (IsActivityCreatorOrReadOnly,)
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
        queryset = Report.objects.all()
        queryset = queryset \
            .annotate(
                is_creator=Case(
                    When(activity__user_id=self.request.user.id, then=Value(True)),
                    default=Value(False)
                ),
                comment_count=Count('comments', distinct=True)
            ) \
            .prefetch_related('location', 'activity', 'comments') \
            .select_related('location', 'activity') \
            .order_by('-id')

        return queryset

    def get_object(self, uuid, is_update=False):
        queryset = self.get_queryset()

        try:
            if is_update:
                queryset = queryset.select_for_update() \
                    .get(uuid=uuid)
            else:
                queryset = queryset.get(uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound()

        return queryset

    def list(self, request, format=None):
        identifier = request.query_params.get('identifier')
        queryset = self.get_queryset()

        if identifier:
            queryset = queryset.filter(identifier=identifier)

        paginator = LimitOffsetPagination()
        paginate_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ListReportSerializer(
            paginate_queryset,
            context=self.context,
            many=True
        )

        results = build_pagination(paginator, serializer)
        return Response(results, status=response_status.HTTP_200_OK)

    def retrieve(self, request, uuid=None, format=None):
        instance = self.get_object(uuid=uuid)
        serializer = RetrieveReportSerializer(
            instance=instance,
            context=self.context
        )
        return Response(serializer.data, status=response_status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, format=None):
        serializer = CreateReportSerializer(
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
    def partial_update(self, request, uuid=None, format=None):
        instance = self.get_object(uuid=uuid, is_update=True)
        self.check_object_permissions(request, instance)

        serializer = UpdateReportSerializer(
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
    def destroy(self, request, uuid=None, format=None):
        instance = self.get_object(uuid=uuid, is_update=True)
        self.check_object_permissions(request, instance)

        # copy for response
        instance_copy = copy(instance)

        # run delete
        instance.delete()

        # return object
        serializer = RetrieveReportSerializer(
            instance_copy,
            context=self.context
        )

        return Response(serializer.data, status=response_status.HTTP_200_OK)
