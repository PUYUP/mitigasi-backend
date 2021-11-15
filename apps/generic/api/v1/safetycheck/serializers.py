from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.urls.base import reverse

from rest_framework import serializers
from rest_framework.exceptions import NotFound
from apps.generic.api.v1.attachment.serializers import RetrieveAttachmentSerializer

from apps.generic.api.v1.location.serializers import CreateLocationSerializer, RetrieveLocationSerializer, UpdateLocationSerializer
from apps.threat.api.v1.hazard.serializers import RetrieveHazardSerializer

SafetyCheck = apps.get_registered_model('generic', 'SafetyCheck')
Attachment = apps.get_registered_model('generic', 'Attachment')
Hazard = apps.get_registered_model('threat', 'Hazard')


class BaseSafetyCheckSerializer(serializers.ModelSerializer):
    authored = serializers.BooleanField(read_only=True)
    activity_author = serializers.CharField(read_only=True)
    _links = serializers.SerializerMethodField()

    class Meta:
        model = SafetyCheck
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context.get('request').user

    def get__links(self, instance):
        request = self.context.get('request')
        self_link = reverse('generic_api:safetycheck-detail',
                            kwargs={'uuid': instance.uuid})
        collection_link = reverse('generic_api:safetycheck-list')

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


class RetrieveSafetyCheckSerializer(BaseSafetyCheckSerializer):
    locations = RetrieveLocationSerializer(many=True)
    attachments = RetrieveAttachmentSerializer(many=True)

    class Meta(BaseSafetyCheckSerializer.Meta):
        pass

    def to_representation(self, instance):
        content_object = getattr(instance, 'content_object')
        data = super().to_representation(instance)

        if content_object:
            if isinstance(content_object, Hazard):
                serializer = RetrieveHazardSerializer(
                    instance=instance.content_object,
                    context=self.context
                )

                data.update({'content_object': serializer.data})
        return data


class ListSafetyCheckSerializer(BaseSafetyCheckSerializer):
    locations = RetrieveLocationSerializer(many=True)
    attachments = RetrieveAttachmentSerializer(many=True)

    class Meta(BaseSafetyCheckSerializer.Meta):
        pass

    def to_representation(self, instance):
        content_object = getattr(instance, 'content_object')
        data = super().to_representation(instance)

        if content_object:
            if isinstance(content_object, Hazard):
                serializer = RetrieveHazardSerializer(
                    instance=instance.content_object,
                    context=self.context,
                    fields=('uuid', 'classify', 'incident',)
                )

                data.update({'content_object': serializer.data})
        return data


class CreateSafetyCheckSerializer(BaseSafetyCheckSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    locations = CreateLocationSerializer(many=True)
    attachments = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=Attachment.objects.all(),
        required=False
    )

    class Meta(BaseSafetyCheckSerializer.Meta):
        fields = ('user', 'condition', 'situation', 'content_type',
                  'object_id', 'locations', 'attachments',)

    def to_internal_value(self, data):
        object_id = data.get('object_id', None)
        content_type = data.get('content_type', None)
        content_type_param = dict()
        content_type_objs = ContentType.objects.filter(model=content_type)

        for ct in content_type_objs:
            model = ct.model_class()
            if model and hasattr(model, 'safetychecks'):
                content_type_param.update({
                    'model': model._meta.model_name,
                    'app_label': model._meta.app_label,
                })

                break

        if content_type_param:
            try:
                content_type_obj = ContentType.objects.get(
                    **content_type_param
                )
            except ObjectDoesNotExist as e:
                raise NotFound(detail=str(e))

            content_object = content_type_obj.get_object_for_this_type(
                uuid=object_id
            )

            data.update({
                'content_type': content_type_obj.id,
                'object_id': content_object.id,
            })

        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = {'authored': True}
        serializer = RetrieveSafetyCheckSerializer(
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

        # if hasattr(self.Meta.model, 'activities'):
        #     Activity = self.Meta.model.activities.field.related_model

        defaults = {
            'situation': validated_data.pop('situation'),
            'condition': validated_data.pop('condition'),
        }

        instance, _created = self.Meta.model.objects \
            .update_or_create(defaults=defaults, **validated_data)

        # don't forget chreate `activity`
        instance.activities.create(user=self.user)

        if instance:
            if locations:
                instance.set_locations(locations)

            if attachments:
                attachments = self.verify_attachments(attachments)
                instance.set_attachments(attachments)

        # refresh...
        instance.refresh_from_db()
        return instance


class UpdateSafetyCheckSerializer(BaseSafetyCheckSerializer):
    locations = UpdateLocationSerializer(many=True)
    attachments = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=Attachment.objects.all(),
        required=False
    )

    class Meta(BaseSafetyCheckSerializer.Meta):
        fields = ('condition', 'situation', 'locations', 'attachments', )

    def to_representation(self, instance):
        serializer = RetrieveSafetyCheckSerializer(
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
