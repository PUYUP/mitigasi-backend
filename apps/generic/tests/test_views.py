import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps
from ..api.v1.comment.serializers import CreateCommentSerializer

Hazard = apps.get_registered_model('threat', 'Hazard')
Comment = apps.get_registered_model('generic', 'Comment')


# initialize the APIClient app
client = Client()
