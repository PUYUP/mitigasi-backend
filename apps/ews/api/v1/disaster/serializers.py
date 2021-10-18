from django.apps import apps
from django.urls import reverse

from rest_framework import serializers

Disaster = apps.get_registered_model('ews', 'Disaster')
DisasterLocation = apps.get_registered_model('ews', 'DisasterLocation')


class BaseDisasterLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisasterLocation
        fields = '__all__'


class BaseDisasterSerializer(serializers.ModelSerializer):
    locations = BaseDisasterLocationSerializer(many=True)
    location_plain = serializers.ListField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    _links = serializers.SerializerMethodField()

    class Meta:
        model = Disaster
        fields = '__all__'

    def get__links(self, instance):
        request = self.context.get('request')
        self_link = reverse('ews_api:disaster-detail',
                            kwargs={'uuid': instance.uuid})
        collection_link = reverse('ews_api:disaster-list')

        return {
            'self': request.build_absolute_uri(self_link),
            'collection': request.build_absolute_uri(collection_link)
        }


class ListDisasterSerializer(BaseDisasterSerializer):
    class Meta(BaseDisasterSerializer.Meta):
        fields = '__all__'


class RetrieveDisasterSerializer(BaseDisasterSerializer):
    class Meta(BaseDisasterSerializer.Meta):
        fields = '__all__'
