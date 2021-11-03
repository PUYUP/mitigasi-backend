from copy import copy

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.apps import apps

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.loading import build_pagination
from .serializers import CreateHazardSerializer, ListHazardSerializer, RetrieveHazardSerializer, UpdateHazardSerializer
from ....permissions import IsHazardCreatorOrReadOnly
from ....models import HAZARD_CLASSIFY_MODEL_MAPPER

Hazard = apps.get_registered_model('threat', 'Hazard')


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
            "classify": "101"
        }


    POST
    -----

        `classify`: default as 999 (other) (optional)
        `incident`: name of hazard (required)
        `occur_at`: valid UTC time format (required)

        {
            "classify": "101",
            "incident": "banjir bro",
            "description": "lipsum",
            "occur_at": "2012-09-04 06:00:00.000000",
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
        'destroy': (IsHazardCreatorOrReadOnly,),
        'partial_update': (IsHazardCreatorOrReadOnly,),
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
        queryset = Hazard.objects \
            .prefetch_related('locations', 'locations__impacts', 'attachments') \
            .order_by('-id')

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
        classify = request.query_params.get('classify')
        queryset = self.get_queryset().filter(landslide__isnull=False)

        if classify:
            try:
                model_name = HAZARD_CLASSIFY_MODEL_MAPPER[classify]._meta.model_name
            except IndexError:
                model_name = None

            if model_name:
                queryset = queryset.filter(
                    **{'%s__isnull' % model_name: False}
                )

        paginator = LimitOffsetPagination()
        paginate_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ListHazardSerializer(
            paginate_queryset,
            context=self.context,
            many=True
        )

        results = build_pagination(paginator, serializer)
        return Response(results, status=response_status.HTTP_200_OK)

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

    def retrieve(self, request, uuid=None):
        instance = self.get_object(uuid=uuid)
        serializer = RetrieveHazardSerializer(
            instance=instance,
            context=self.context
        )

        return Response(serializer.data, status=response_status.HTTP_200_OK)

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
