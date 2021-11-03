from django.utils.translation import gettext_lazy as _

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class RootAPIView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (AnonRateThrottle, UserRateThrottle,)

    def get(self, request, format=None):
        return Response({
            'person': {
                'securecode': reverse('person_api:securecode-list', request=request,
                                      format=format, current_app='person'),
                'user': reverse('person_api:user-list', request=request,
                                format=format, current_app='person'),
                'password-recovery': reverse('person_api:password-recovery', request=request,
                                             format=format, current_app='person'),
                'token': reverse('person_api:token-obtain', request=request,
                                 format=format, current_app='person'),
            },
            'ews': {
                'scraper-bnpb-dipi': reverse('ews_api:scraper-bnpb-dipi', request=request,
                                             format=format, current_app='ews'),
                'scraper-bmkg-tews': reverse('ews_api:scraper-bmkg-tews', request=request,
                                             format=format, current_app='ews'),
                'scraper-bmkg-tews-recent': reverse('ews_api:scraper-bmkg-tews-recent', request=request,
                                                    format=format, current_app='ews'),
                'scraper-bmkg-tews-realtime': reverse('ews_api:scraper-bmkg-tews-realtime', request=request,
                                                      format=format, current_app='ews'),
                'disaster': reverse('ews_api:disaster-list', request=request,
                                    format=format, current_app='ews'),
            },
            'contribution': {
                'report': reverse('contribution_api:report-list', request=request,
                                  format=format, current_app='contribution'),
                'comment': reverse('contribution_api:comment-list', request=request,
                                   format=format, current_app='contribution'),
            },
            'threat': {
                'hazard': reverse('threat_api:hazard-list', request=request,
                                  format=format, current_app='threat'),
            },
            'generic': {
                'attachment': reverse('generic_api:attachment-list', request=request,
                                      format=format, current_app='generic'),
            },
        })
