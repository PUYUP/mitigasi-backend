from rest_framework import status as response_status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ..target.bmkg_earthquake import quake_feeled, quake_recent
from ..target.bnpb_dibi import dibi


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def bmkg_earthquake_feeled(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        return Response('OK')

    elif request.method == 'POST':
        # quake_feeled()
        return Response('OK', status=response_status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def bmkg_earthquake_recent(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        return Response('OK')

    elif request.method == 'POST':
        # quake_recent()
        return Response('OK', status=response_status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def bnpb_dibi(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        return Response('OK')

    elif request.method == 'POST':
        # dibi(request=request)
        return Response('OK', status=response_status.HTTP_201_CREATED)
