from django.apps import apps
from django.db import transaction
from django.db.models import Q
from django.db.models.aggregates import Count
from django.urls import reverse

from rest_framework import serializers
from apps.generic.api.v1.activity.serializers import GeneralModelSerializer

from apps.generic.api.v1.attachment.serializers import RetrieveAttachmentSerializer
from apps.generic.api.v1.location.serializers import (
    CreateLocationSerializer,
    RetrieveLocationSerializer,
    UpdateLocationSerializer
)
from apps.threat.models import DISASTER_CLASSIFY_MODEL_MAPPER as mapper
from core.drf_helpers import DynamicFieldsModelSerializer

Hazard = apps.get_registered_model('threat', 'Hazard')
Attachment = apps.get_registered_model('generic', 'Attachment')


class BaseHazardSerializer(DynamicFieldsModelSerializer):
    authored = serializers.BooleanField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    safetycheck_affected_count = serializers.IntegerField(read_only=True)
    safetycheck_safe_count = serializers.IntegerField(read_only=True)
    safetycheck_confirmed = serializers.BooleanField(read_only=True)
    _links = serializers.SerializerMethodField()

    class Meta:
        model = Hazard
        fields = '__all__'

    def get__links(self, instance):
        request = self.context.get('request')
        self_link = reverse('threat_api:hazard-detail',
                            kwargs={'uuid': instance.uuid})
        collection_link = reverse('threat_api:hazard-list')

        return {
            'self': request.build_absolute_uri(self_link),
            'collection': request.build_absolute_uri(collection_link)
        }

    def verify_attachments(self, attachments):
        # make sure `attachments` owned by current user
        user = self.context.get('request').user

        return [
            x for x in attachments if getattr(x, 'activities')
            and (x.activities.first().user.id == user.id)
        ]

    def disaster_serializer(self, model):
        GeneralModelSerializer.Meta.model = model
        return GeneralModelSerializer


class RetrieveHazardSerializer(BaseHazardSerializer):
    locations = RetrieveLocationSerializer(many=True)
    attachments = RetrieveAttachmentSerializer(many=True)
    source = serializers.SerializerMethodField()
    classify_display = serializers.CharField()

    class Meta(BaseHazardSerializer.Meta):
        fields = '__all__'

    def get_source(self, obj):
        if obj.source:
            return obj.source
        return obj.activity_author

    def to_representation(self, instance):
        request = self.context.get('request')
        data = super().to_representation(instance)

        # serializing disaster
        for classify, model in mapper.items():
            model_name = model._meta.model_name

            if hasattr(instance, model_name):
                model_object = getattr(instance, model_name)
                if model_object:
                    serializer = self.disaster_serializer(model)
                    serializer_data = serializer(
                        instance=model_object,
                        context=self.context
                    ).data

                    data.update({'disaster': serializer_data})

        # some cases this will needed
        # egg create `safetycheck` will return `hazard`
        # with new safetychek value
        if (
            'safetycheck_affected_count' not in data or
            'safetycheck_safe_count' not in data
        ):
            confirmed = instance.safetychecks \
                .filter(activities__user_id=request.user.id)

            safetychecks = instance.safetychecks \
                .aggregate(
                    safetycheck_affected_count=Count(
                        'id',
                        filter=Q(condition='affected')
                    ),
                    safetycheck_safe_count=Count(
                        'id',
                        filter=Q(condition='safe')
                    )
                )

            data.update(safetychecks)
            data.update({'safetycheck_confirmed': confirmed.exists()})

        return data


class ListHazardSerializer(RetrieveHazardSerializer):
    class Meta(RetrieveHazardSerializer.Meta):
        fields = '__all__'


class CreateHazardSerializer(BaseHazardSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    locations = CreateLocationSerializer(many=True, required=False)
    attachments = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=Attachment.objects.all(),
        required=False
    )

    class Meta(BaseHazardSerializer.Meta):
        fields = ('user', 'classify', 'incident', 'description',
                  'occur_at', 'source', 'locations', 'attachments',)

    def to_representation(self, instance):
        data = {'authored': True}
        serializer = RetrieveHazardSerializer(
            instance=instance,
            context=self.context
        )
        data.update(serializer.data)

        return data

    @transaction.atomic
    def create(self, validated_data):
        """`activity` must create before all of childs method
        such as `attachments`, etc"""

        locations = validated_data.pop('locations', None)
        attachments = validated_data.pop('attachments', None)
        defaults = {
            'user': validated_data.pop('user'),
            'description': validated_data.pop('description')
        }

        instance, created = self.Meta.model.objects \
            .get_or_create(defaults=defaults, **validated_data)

        # don't forget chreate `activity`
        if created:
            user = self.context.get('request').user
            instance.activities.create(user=user)

            if instance:
                if locations:
                    instance.set_locations(locations)

                if attachments:
                    attachments = self.verify_attachments(attachments)
                    instance.set_attachments(attachments)

        # refresh...
        instance.refresh_from_db()
        return instance


class UpdateHazardSerializer(CreateHazardSerializer):
    locations = UpdateLocationSerializer(many=True)

    class Meta(CreateHazardSerializer.Meta):
        pass

    def to_representation(self, instance):
        serializer = RetrieveHazardSerializer(
            instance=instance,
            context=self.context
        )

        return serializer.data

    @transaction.atomic
    def update(self, instance, validated_data):
        locations = validated_data.pop('locations', None)
        attachments = validated_data.pop('attachments', None)
        instance = super().update(instance, validated_data)

        if locations:
            instance.set_locations(locations)

        if attachments:
            attachments = self.verify_attachments(attachments)
            instance.set_attachments(attachments)

        instance.refresh_from_db()
        return instance
