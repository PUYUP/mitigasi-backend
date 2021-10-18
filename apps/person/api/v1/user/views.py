from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from django.apps import apps

from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import viewsets, status as response_status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CreateUserSerializer,
    ListUserSerializer,
    RetrieveUserSerializer,
    TokenObtainPairSerializerExtend,
    UpdateUserSerializer
)
from ..profile.serializers import UpdateProfileSerializer
from ..password.serializers import ChangePasswordSerializer
from ....helpers import build_result_pagination

UserModel = get_user_model()
Profile = apps.get_model('person', 'Profile')

# Define to avoid used ...().paginate__
_PAGINATOR = LimitOffsetPagination()


class BaseViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.context = dict()

    def initialize_request(self, request, *args, **kwargs):
        self.context.update({'request': request})
        return super().initialize_request(request, *args, **kwargs)


class UserViewSet(BaseViewSet):
    """
    POST
    -----
        {
            "email": "required",
            "username": "required",
            "password": "required",
            "retype_password": "required",
            "validation": {
                "passcode": "1451AA",
                "token": "020252 522",
                "challenge": "validate_email"
            }
        }


    PATCH
    -----
        {
            "email": "mychange@email.com",
            "msisdn": "08295222622",
            "username": "admino",
            "validation": {
                "passcode": "1451AA",
                "token": "020252 522",
                "challenge": "validate_email"
            }
        }
    """
    lookup_field = 'hexid'
    throttle_classes = (AnonRateThrottle, UserRateThrottle,)
    permission_classes = (AllowAny,)
    permission_action = {
        'create': (AllowAny,),
        'partial_update': (IsAuthenticated,),
        'list': (IsAuthenticated,),
        'retrieve': (IsAuthenticated,),
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

    def queryset(self):
        return UserModel.objects.all()

    def queryset_instance(self, hexid, for_update=False):
        try:
            if for_update:
                return self.queryset().select_for_update().get(hexid=hexid)
            return self.queryset().get(hexid=hexid)
        except ObjectDoesNotExist:
            raise NotFound()

    @transaction.atomic
    def create(self, request, format=None):
        serializer = CreateUserSerializer(
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
    def partial_update(self, request, hexid=None, format=None):
        instance = self.queryset_instance(hexid, for_update=True)
        serializer = UpdateUserSerializer(
            instance,
            data=request.data,
            context=self.context,
            partial=True
        )

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except DjangoValidationError as e:
                raise ValidationError(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)

    def list(self, request, format=None):
        queryset = self.queryset()
        paginator = _PAGINATOR.paginate_queryset(queryset, request)
        serializer = ListUserSerializer(
            paginator,
            context=self.context,
            many=True
        )

        results = build_result_pagination(self, _PAGINATOR, serializer)
        return Response(results, status=response_status.HTTP_200_OK)

    def retrieve(self, request, hexid=None, format=None):
        try:
            instance = self.queryset_instance(hexid=hexid)
        except ObjectDoesNotExist:
            raise NotFound()

        # limit fields when other user see the user
        fields = None
        if str(request.user.hexid) != hexid:
            fields = ('hexid', 'name', 'username', 'profile',)

        serializer = RetrieveUserSerializer(
            instance,
            context=self.context,
            fields=fields
        )

        return Response(serializer.data, status=response_status.HTTP_200_OK)

    # update profile
    @transaction.atomic
    @action(
        detail=True,
        methods=['patch'],
        url_name='profile',
        url_path='profile',
        permission_classes=(IsAuthenticated,),
        parser_classes=(JSONParser, MultiPartParser,)
    )
    def update_profile(self, request, hexid=None, format=None):
        try:
            instance = Profile.objects \
                .select_for_update() \
                .get(user__hexid=hexid, user_id=request.user.id)
        except ObjectDoesNotExist:
            raise NotFound()

        serializer = UpdateProfileSerializer(
            instance,
            data=request.data,
            context=self.context,
            partial=True
        )

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except DjangoValidationError as e:
                raise ValidationError(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)

    # change password
    @transaction.atomic
    @action(
        detail=True,
        methods=['post'],
        url_name='change-password',
        url_path='change-password',
        permission_classes=(IsAuthenticated,),
    )
    def change_password(self, request, hexid=None, format=None):
        serializer = ChangePasswordSerializer(
            request.user,
            data=request.data,
            context=self.context
        )

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except DjangoValidationError as e:
                raise ValidationError(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)


class TokenObtainPairViewExtend(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializerExtend

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        except ValueError as e:
            raise ValidationError({'detail': str(e)})

        return Response(serializer.validated_data, status=response_status.HTTP_200_OK)
