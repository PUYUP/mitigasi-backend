from django.apps import apps
from rest_framework import serializers

Impact = apps.get_registered_model('generic', 'Impact')


class BaseImpactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Impact
        fields = '__all__'


class RetrieveImpactSerializer(BaseImpactSerializer):
    class Meta(BaseImpactSerializer.Meta):
        fields = '__all__'


class CreateImpactSerializer(BaseImpactSerializer):
    class Meta(BaseImpactSerializer.Meta):
        fields = ('identifier', 'value', 'metric', 'description',)


class UpdateImpactSerializer(BaseImpactSerializer):
    uuid = serializers.UUIDField(required=False)

    class Meta(BaseImpactSerializer.Meta):
        fields = ('uuid', 'identifier', 'value', 'metric', 'description',)
