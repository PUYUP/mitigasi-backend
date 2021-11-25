from django.db import transaction

from rest_framework import status as response_status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..target.bmkg_earthquake import quake_feeled, quake_recent
from ..target.bnpb_dibi import dibi
from ..target.bmkg_social_media import ews_bmkg, twitter


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def bmkg_earthquake_feeled_view(request):
    if request.user.is_superuser:
        quake_feeled()
    return Response('OK', status=response_status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def bmkg_earthquake_recent_view(request):
    if request.user.is_superuser:
        quake_recent()
    return Response('OK', status=response_status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def bnpb_dibi_view(request):
    if request.user.is_superuser:
        dibi(param=request.data, request=request)
    return Response('OK', status=response_status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def twitter_bmkg_view(request):
    if request.user.is_superuser:
        twitter(param=request.data, request=request)
    return Response('OK', status=response_status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def ews_bmkg_view(request):
    if request.user.is_superuser:
        ews_bmkg(request=request)
    return Response('OK', status=response_status.HTTP_201_CREATED)
