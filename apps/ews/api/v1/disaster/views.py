from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Count

from rest_framework import viewsets, status as response_status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import NotFound

from core.loading import build_pagination

from .serializers import ListDisasterSerializer, RetrieveDisasterSerializer

Disaster = apps.get_registered_model('ews', 'Disaster')


class BaseViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.context = dict()

    def initialize_request(self, request, *args, **kwargs):
        self.context.update({'request': request})
        return super().initialize_request(request, *args, **kwargs)


class DisasterAPIViewSet(BaseViewSet):
    """
    GET
    -----

        {
            "identifier": "101",
            "status": "preliminary",
            "source": "bmkg"
        }

    """

    lookup_field = 'uuid'
    permission_classes = (AllowAny,)
    throttle_classes = (AnonRateThrottle, UserRateThrottle,)

    def get_queryset(self):
        queryset = Disaster.objects.all()
        queryset = queryset \
            .annotate(comment_count=Count('comments', distinct=True)) \
            .prefetch_related('locations', 'comments') \
            .order_by('-occur_at')

        return queryset

    def list(self, request, format=None):
        queryset = self.get_queryset()

        identifier = request.query_params.get('identifier')
        status = request.query_params.get('status')
        source = request.query_params.get('source')

        if identifier:
            queryset = queryset.filter(identifier=identifier)

        if status:
            queryset = queryset.filter(eav__disaster_status=status)
        else:
            queryset = queryset.exclude(eav__disaster_status='preliminary')

        if source:
            queryset = queryset.filter(source__icontains=source)

        paginator = LimitOffsetPagination()
        paginate_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ListDisasterSerializer(
            paginate_queryset,
            context=self.context,
            many=True
        )

        results = build_pagination(paginator, serializer)
        return Response(results, status=response_status.HTTP_200_OK)

    def retrieve(self, request, uuid=None, format=None):
        try:
            queryset = self.get_queryset().get(uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound()

        serializer = RetrieveDisasterSerializer(
            instance=queryset,
            context=self.context
        )
        return Response(serializer.data, status=response_status.HTTP_200_OK)
