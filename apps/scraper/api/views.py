from django.db import transaction

from rest_framework import status as response_status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ..target.bmkg_earthquake import quake_feeled, quake_recent
from ..target.bnpb_dibi import dibi
from ..target.bmkg_social_media import twitter


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@transaction.atomic
def bmkg_earthquake_feeled(request):
    if request.method == 'GET':
        return Response('OK')

    elif request.method == 'POST':
        if request.user.is_superuser:
            quake_feeled()
        return Response('OK', status=response_status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@transaction.atomic
def bmkg_earthquake_recent(request):
    if request.method == 'GET':
        return Response('OK')

    elif request.method == 'POST':
        if request.user.is_superuser:
            quake_recent()
        return Response('OK', status=response_status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@transaction.atomic
def bnpb_dibi(request):
    if request.method == 'GET':
        return Response('OK')

    elif request.method == 'POST':
        if request.user.is_superuser:
            dibi(param=request.data, request=request)
        return Response('OK', status=response_status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@transaction.atomic
def twitter_bmkg(request):
    if request.method == 'GET':
        return Response('OK')

    elif request.method == 'POST':
        if request.user.is_superuser:
            twitter(param=request.data, request=request)
        return Response('OK', status=response_status.HTTP_201_CREATED)
