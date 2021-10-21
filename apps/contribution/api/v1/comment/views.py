from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Count
from django.db.models.expressions import Case, Value, When

from rest_framework import viewsets, status as response_status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import NotFound, ValidationError

from core.loading import build_pagination

from .serializers import CreateCommentSerializer, ListCommentSerializer, RetrieveCommentSerializer

Comment = apps.get_registered_model('contribution', 'Comment')


class BaseViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.context = dict()

    def initialize_request(self, request, *args, **kwargs):
        self.context.update({'request': request})
        return super().initialize_request(request, *args, **kwargs)


class CommentAPIViewSet(BaseViewSet):
    """
    POST
    -----

        {
            "applied_uuid": "b4212315-960a-46fb-8b97-9683ae835047",
            "applied_model": "report",
            "description": "test child comment",
            "parent": "b1adb92f-5e1c-4880-95f6-cb7966395d6b"
        }


    GET
    -----

        {
            "applied_uuid": "b4212315-960a-46fb-8b97-9683ae835047",
            "applied_model": "report",
            "parent": "b1adb92f-5e1c-4880-95f6-cb7966395d6b"
        }
    """
    lookup_field = 'uuid'
    throttle_classes = (AnonRateThrottle, UserRateThrottle,)
    permission_classes = (IsAuthenticated,)
    permission_action = {
        'list': (AllowAny,),
        'retrieve': (AllowAny,),
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
        queryset = Comment.objects.all()
        queryset = queryset \
            .annotate(
                is_creator=Case(
                    When(activity__user_id=self.request.user.id, then=Value(True)),
                    default=Value(False)
                ),
                comment_count=Count('childs', distinct=True)
            ) \
            .prefetch_related('content_type', 'activity', 'activity__user') \
            .select_related('content_type', 'activity', 'activity__user') \
            .order_by('-id')

        return queryset

    def list(self, request, format=None):
        applied_uuid = request.query_params.get('applied_uuid')
        applied_model = request.query_params.get('applied_model')
        parent = request.query_params.get('parent')

        queryset = self.get_queryset()

        if parent:
            # child
            queryset = queryset.filter(childs__parent__uuid=parent)
        else:
            # root
            queryset = queryset.filter(parents__isnull=True)

        if applied_uuid and applied_model:
            applied_model = applied_model.lower()
            ct_obj = ContentType.objects.get(model=applied_model)
            content_object = ct_obj.get_object_for_this_type(uuid=applied_uuid)

            queryset = queryset.filter(
                content_type__model=applied_model,
                object_id=content_object.id
            )

        paginator = LimitOffsetPagination()
        paginate_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ListCommentSerializer(
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

        serializer = RetrieveCommentSerializer(
            instance=queryset,
            context=self.context
        )
        return Response(serializer.data, status=response_status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, format=None):
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
