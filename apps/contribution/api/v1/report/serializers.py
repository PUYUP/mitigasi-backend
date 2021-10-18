from django.apps import apps
from django.urls import reverse
from django.db import transaction

from rest_framework import serializers
from apps.contribution.mixins.activity_mixin import ActivityCreateMixin

Report = apps.get_registered_model('contribution', 'Report')
ReportLocation = apps.get_registered_model('contribution', 'ReportLocation')


class BaseReportLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportLocation
        fields = '__all__'


class CreateReportLocationSerializer(BaseReportLocationSerializer):
    class Meta(BaseReportLocationSerializer.Meta):
        fields = ('latitude', 'longitude', 'country',
                  'country_code', 'administrative_area',
                  'sub_administrative_area', 'locality',
                  'sub_locality', 'thoroughfare',
                  'sub_thoroughfare', 'areas_of_interest',
                  'postal_code',)
        extra_kwargs = {
            'latitude': {'required': True},
            'longitude': {'required': True},
        }


class BaseReportSerializer(serializers.ModelSerializer):
    is_creator = serializers.BooleanField(read_only=True)
    location = BaseReportLocationSerializer(many=False)
    location_plain = serializers.ListField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    _links = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Report
        fields = '__all__'

    def get__links(self, instance):
        request = self.context.get('request')
        self_link = reverse('contribution_api:report-detail',
                            kwargs={'uuid': instance.uuid})
        collection_link = reverse('contribution_api:report-list')

        return {
            'self': request.build_absolute_uri(self_link),
            'collection': request.build_absolute_uri(collection_link)
        }


class ListReportSerializer(BaseReportSerializer):
    class Meta(BaseReportSerializer.Meta):
        fields = '__all__'


class RetrieveReportSerializer(BaseReportSerializer):
    class Meta(BaseReportSerializer.Meta):
        fields = '__all__'


class CreateReportSerializer(ActivityCreateMixin, BaseReportSerializer):
    location = CreateReportLocationSerializer(many=False)

    class Meta(BaseReportSerializer.Meta):
        fields = ('identifier', 'title', 'occur_at', 'description',
                  'reason', 'chronology', 'necessary', 'location',)
        kwargs = {
            'identifier': {'required': True, 'allow_blank': False}
        }

    def to_representation(self, instance):
        initial = {'is_creator': True}
        serializer = RetrieveReportSerializer(
            instance=instance,
            context=self.context
        )
        initial.update(serializer.data)

        return initial

    @transaction.atomic
    def create(self, validated_data):
        location = validated_data.pop('location', None)
        instance = self.Meta.model.objects.create(**validated_data)
        ReportLocation.objects.create(report=instance, **location)
        return instance


class UpdateReportSerializer(BaseReportSerializer):
    class Meta(BaseReportSerializer.Meta):
        fields = ('title', 'description', 'reason', 'chronology', 'necessary',)

    def to_representation(self, instance):
        serializer = RetrieveReportSerializer(
            instance=instance,
            context=self.context
        )
        return serializer.data
