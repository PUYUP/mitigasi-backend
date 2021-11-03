import uuid

from django.apps import apps
from django.db import transaction
from django.urls import reverse
from django.core.files.base import ContentFile

from rest_framework import serializers

Hazard = apps.get_registered_model('threat', 'Hazard')
Location = apps.get_registered_model('generic', 'Location')
Impact = apps.get_registered_model('generic', 'Impact')
Attachment = apps.get_registered_model('generic', 'Attachment')


"""
Impact Serializer
"""


class ImpactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Impact
        fields = ('identifier', 'value', 'metric', 'description',)

    @transaction.atomic
    def to_internal_valuex(self, data):
        data = super().to_internal_value(data)
        return self.Meta.model.objects.create(**data)


class ImpactFieldSerializer(serializers.Serializer):
    # update purpose
    uuid = serializers.UUIDField(required=False)
    delete = serializers.BooleanField(required=False, allow_null=True)

    identifier = serializers.CharField()
    value = serializers.CharField()
    metric = serializers.CharField()
    description = serializers.CharField(required=False)


class ImpactModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Impact
        fields = '__all__'


"""
Location Serializer
"""


class LocationSerializer(serializers.ModelSerializer):
    impacts = ImpactSerializer(many=True, required=False)

    class Meta:
        model = Location
        fields = ('latitude', 'longitude', 'impacts',)

    @transaction.atomic
    def to_internal_valuex(self, data):
        data = super().to_internal_value(data)
        impacts = data.pop('impacts', None)

        instance, _created = self.Meta.model.objects.update_or_create(**data)

        if impacts:
            instance.impacts.set(impacts)

        return instance


class LocationFieldSerialiser(serializers.Serializer):
    # update purpose
    uuid = serializers.UUIDField(required=False)
    delete = serializers.BooleanField(required=False, allow_null=True)

    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    impacts = ImpactFieldSerializer(many=True)


class LocationModelSerializer(serializers.ModelSerializer):
    impacts = ImpactModelSerializer(many=True)

    class Meta:
        model = Location
        fields = '__all__'


class LocationObjectRelatedFieldSerializer(serializers.RelatedField):
    def to_representation(self, value):
        serializer = LocationModelSerializer(value, context=self.context)
        return serializer.data


"""
Hazard Serializer
"""


class BaseHazardSerializer(serializers.ModelSerializer):
    _links = serializers.SerializerMethodField()
    attachments = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=Attachment.objects.all(),
        required=False
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context.get('request').user

    def verify_owned_attachments(self, attachments):
        return [
            x for x in attachments if getattr(x, 'activities')
            and (x.activities.first().user.id == self.user.id)
        ]

    @transaction.atomic
    def remove_attachments(self, instance, attachments):
        # make user `attachments` owned by current user
        attachments = self.verify_owned_attachments(attachments)

        for attachment in attachments:
            # attachments.delete()
            instance.attachments.remove(attachment)

    @transaction.atomic
    def set_attachments(self, instance, attachments):
        # make user `attachments` owned by current user
        attachments = self.verify_owned_attachments(attachments)

        # attachments without `hazard`
        attachments_without_hazard = [
            x for x in attachments if not x.hazard.exists()
        ]

        # attachments has `hazard`
        attachments_with_hazard = [
            x for x in attachments if x.hazard.exists()
        ]

        # create new attachments if they has `hazard`
        if len(attachments_with_hazard) > 0:
            new_attachments = list()

            # just copied it then reupload file
            for attachment in attachments_with_hazard:
                attachment.pk = None
                attachment.uuid = uuid.uuid4()
                attachment.file = ContentFile(
                    attachment.file.read(),
                    name=attachment.file.name
                )

                attachment.save()
                new_attachments.append(attachment)

            # set as new attachments
            instance.attachments.set(new_attachments, bulk=True)

        # set only
        if len(attachments_without_hazard) > 0:
            instance.attachments.set(attachments_without_hazard, bulk=True)


class RetrieveHazardSerializer(BaseHazardSerializer):
    locations = LocationObjectRelatedFieldSerializer(many=True, read_only=True)
    source = serializers.SerializerMethodField()
    classify_display = serializers.CharField()

    class Meta(BaseHazardSerializer.Meta):
        fields = '__all__'

    def get_source(self, obj):
        if obj.source:
            return obj.source
        return obj.author_name


class ListHazardSerializer(RetrieveHazardSerializer):
    class Meta(RetrieveHazardSerializer.Meta):
        fields = '__all__'


class CreateHazardSerializer(BaseHazardSerializer):
    locations = LocationSerializer(many=True, required=False)

    class Meta(BaseHazardSerializer.Meta):
        fields = ('classify', 'incident', 'description',
                  'occur_at', 'locations', 'attachments',)

    def to_representation(self, instance):
        serializer = RetrieveHazardSerializer(
            instance=instance,
            context=self.context
        )

        return serializer.data

    @transaction.atomic
    def create(self, validated_data):
        locations = validated_data.pop('locations', None)
        instance = self.Meta.model.objects.create(**validated_data)

        if locations and instance:
            instance.set_locations(locations)

        # don't forget chreate `activity`
        instance.activities.create(user=self.user)

        # refresh...
        instance.refresh_from_db()
        return instance

    @transaction.atomic
    def createx(self, validated_data):
        locations = validated_data.pop('locations', None)
        instance = self.Meta.model.objects.create(**validated_data)

        if locations:
            instance.locations.set(locations)

        # don't forget create `activity`
        instance.activities.create(user=self.user)
        return instance

    @transaction.atomic
    def creates(self, validated_data):
        attachments = validated_data.pop('attachments', [])
        locations = validated_data.pop('locations', [])
        impacts = [x.pop('impacts', []) for x in locations]

        # create hazard
        instance = self.Meta.model.objects.create(**validated_data)

        # set attachments
        if len(attachments) > 0:
            self.set_attachments(instance, attachments)

        # make locations as object
        locations_objs = [
            instance.locations.model(content_object=instance, **x) for x in locations
        ]

        # create the locations
        locations_id = [
            x.get('id') for x in instance.locations.bulk_create_return_id(locations_objs)
        ]

        # create impacts for each locations
        impacts_objs = list()
        impact_model = None

        for i, v in enumerate(instance.locations.filter(id__in=locations_id)):
            # get impact model
            if i == 0:
                impact_model = v.impacts.model

            for x, y in enumerate(impacts[i]):
                impacts_objs.append(v.impacts.model(content_object=v, **y))

        if impact_model and len(impacts_objs) > 0:
            impact_model.objects.bulk_create(impacts_objs)

        # create `activity`
        instance.activities.create(user=self.user)
        return instance


class UpdateHazardSerializer(CreateHazardSerializer):
    remove_attachments = serializers.SlugRelatedField(
        slug_field='uuid',
        many=True,
        queryset=Attachment.objects.all(),
        required=False
    )

    class Meta(CreateHazardSerializer.Meta):
        fields = ('classify', 'incident', 'description',
                  'occur_at', 'locations', 'attachments', 'remove_attachments',)

    @transaction.atomic
    def update(self, instance, validated_data):
        locations = validated_data.pop('locations', None)
        instance = super().update(instance, validated_data)

        if locations:
            instance.set_locations(locations)

        instance.refresh_from_db()
        return instance

    @transaction.atomic
    def updatex(self, instance, validated_data):
        """
        Masalahnya adalah ketika `impacts` ada di `locations` yang belum
        tersimpan. Locations baru tidak memiliki impacts walaupun telah diset.
        """
        attachments = validated_data.pop('attachments', [])
        remove_attachments = validated_data.pop('remove_attachments', [])
        locations = validated_data.pop('locations', [])
        impacts = [x.pop('impacts', []) for x in locations]

        instance = super().update(instance, validated_data)

        # set attachments
        if len(attachments) > 0:
            self.set_attachments(instance, attachments)

        # delete attachments
        if len(remove_attachments) > 0:
            self.remove_attachments(instance, remove_attachments)

        # Maps for id->instance and id->data item.
        locations_mapping = {x.uuid: x for x in instance.locations.all()}
        locations_data_mapping = {
            x.get('uuid', None): x for x in locations if not x.get('delete', False)
        }

        # Perform locations delete.
        locations_delete_uuids = [
            x.get('uuid', None) for x in locations if x.get('delete', False)
        ]

        if len(locations_delete_uuids) > 0:
            locations_delete_instance = instance.locations \
                .filter(uuid__in=locations_delete_uuids)

            if locations_delete_instance.exists():
                locations_delete_instance.delete()

        # Perform locations creations and updates.
        locations_update = list()
        locations_update_fields = list()
        locations_create = list()

        for index, (uuid, data) in enumerate(locations_data_mapping.items()):
            # remove unused field
            data.pop('uuid', None)

            # get current location
            location_obj = locations_mapping.get(uuid)

            # START IMPACTS
            if location_obj:
                impacts_mapping = {
                    x.uuid: x for x in location_obj.impacts.all()
                }

                impacts_data_mapping = {
                    x.get('uuid', None): x for x in impacts[index]
                }

                impacts_update = list()
                impacts_update_fields = list()
                impacts_create = list()

                for impact_uuid, impact_data in impacts_data_mapping.items():
                    # remove uuid
                    impact_data.pop('uuid', None)

                    # get current impact
                    impact_obj = impacts_mapping.get(impact_uuid, None)

                    if impact_obj:
                        # update
                        for x in impact_data:
                            setattr(impact_obj, x, impact_data.get(x))
                            impacts_update_fields.append(x)
                        impacts_update.append(impact_obj)
                    else:
                        # create
                        impacts_create.append(
                            location_obj.impacts.model(
                                content_object=location_obj,
                                **impact_data
                            )
                        )

                if len(impacts_update) > 0:
                    location_obj.impacts.bulk_update(
                        impacts_update,
                        fields=impacts_update_fields
                    )

                if len(impacts_create) > 0:
                    _impacts_id = [
                        x.get('id') for x in location_obj.impacts.bulk_create_return_id(impacts_create)
                    ]

                # END OF IMPACTS

            if location_obj:
                # update
                for x in data:
                    setattr(location_obj, x, data.get(x))
                    locations_update_fields.append(x)
                locations_update.append(location_obj)
            else:
                # create
                locations_create.append(
                    instance.locations.model(content_object=instance, **data)
                )

        # perform location update
        if len(locations_update) > 0:
            instance.locations.bulk_update(
                locations_update,
                fields=locations_update_fields
            )

        # perform location create
        # create the locations
        if len(locations_create) > 0:
            locations_id = [
                x.get('id') for x in instance.locations.bulk_create_return_id(locations_create)
            ]

            print(instance.locations.filter(id__in=locations_id).count())
            print(len(impacts))
        instance.refresh_from_db()
        return instance
