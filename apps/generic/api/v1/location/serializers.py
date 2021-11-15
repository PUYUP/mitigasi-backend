from django.apps import apps
from rest_framework import serializers

from apps.generic.api.v1.impact.serializers import (
    CreateImpactSerializer,
    RetrieveImpactSerializer,
    UpdateImpactSerializer
)

Location = apps.get_registered_model('generic', 'Location')


class BaseLocationSerializer(serializers.ModelSerializer):
    impacts = CreateImpactSerializer(
        many=True,
        required=False,
        allow_empty=False,
        allow_null=True
    )

    class Meta:
        model = Location
        fields = '__all__'


class RetrieveLocationSerializer(BaseLocationSerializer):
    impacts = RetrieveImpactSerializer(many=True, read_only=True)

    class Meta(BaseLocationSerializer.Meta):
        fields = '__all__'


class CreateLocationSerializer(BaseLocationSerializer):
    class Meta(BaseLocationSerializer.Meta):
        fields = ('latitude', 'longitude', 'locality', 'impacts',)


class UpdateLocationSerializer(BaseLocationSerializer):
    uuid = serializers.UUIDField(required=False)
    impacts = UpdateImpactSerializer(
        many=True,
        required=False,
        allow_empty=True,
        allow_null=True
    )

    class Meta(BaseLocationSerializer.Meta):
        fields = ('uuid', 'latitude', 'longitude', 'locality', 'impacts',)
