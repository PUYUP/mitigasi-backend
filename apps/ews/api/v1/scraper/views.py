from django.db import transaction

from rest_framework import status as response_status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from apps.ews.scraper import bnpb, bmkg


class BNPB_DIBI_ScraperAPIView(APIView):
    """
    Param;

        {
            "fetch": "all", // only for staff
            "identifier": "108", // kode bencana
            "start": 0 // mulai item ke
        }

    """
    permission_classes = (AllowAny,)
    throttle_classes = (AnonRateThrottle, UserRateThrottle,)

    def get(self, request, format=None):
        return Response(status=response_status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, format=None):
        param = request.data
        scrape = bnpb.dibi(param, request)
        if not scrape:
            return Response({'has_data': False}, status=response_status.HTTP_200_OK)
        return Response({'has_data': True}, status=response_status.HTTP_201_CREATED)


class BMKG_TEWS_ScraperAPIView(APIView):
    """
    Param;

        {}

    """
    permission_classes = (AllowAny,)
    throttle_classes = (AnonRateThrottle, UserRateThrottle,)

    def get(self, request, format=None):
        return Response(status=response_status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, format=None):
        param = request.data
        scrape = bmkg.quake()

        return Response(status=response_status.HTTP_200_OK)
