from django.db import transaction

from rest_framework import status as response_status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from apps.ews.scraper import bnpb


class BNPB_DIBI_ScraperAPIView(APIView):
    """
    Param;

        {
            "jn": "108", // kode bencana
            "start": 30 // mulai item ke
        }

    """
    permission_classes = (AllowAny,)
    throttle_classes = (AnonRateThrottle, UserRateThrottle,)

    def get(self, request, format=None):
        return Response(status=response_status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, format=None):
        param = request.data
        scrape = bnpb.dibi(param)
        if scrape is None:
            return Response({'has_data': False}, status=response_status.HTTP_200_OK)
        return Response({'has_data': True}, status=response_status.HTTP_201_CREATED)
