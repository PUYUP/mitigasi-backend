from django.apps import apps
from django.urls.base import reverse

from rest_framework import serializers

from apps.threat.models import DISASTER_CLASSIFY_MODEL_MAPPER
from core.drf_helpers import GeneralModelSerializer

Activity = apps.get_registered_model('generic', 'Activity')


class BaseActivitySerializer(serializers.ModelSerializer):
    authored = serializers.BooleanField(read_only=True)
    _links = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = '__all__'

    def get__links(self, instance):
        request = self.context.get('request')
        self_link = reverse('generic_api:activity-detail',
                            kwargs={'uuid': instance.uuid})
        collection_link = reverse('generic_api:activity-list')

        return {
            'self': request.build_absolute_uri(self_link),
            'collection': request.build_absolute_uri(collection_link)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context.get('request').user


class ListActivitySerializer(BaseActivitySerializer):
    def disaster_serializer(self, model):
        GeneralModelSerializer.Meta.model = model
        return GeneralModelSerializer

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for classify, model in DISASTER_CLASSIFY_MODEL_MAPPER.items():
            model_name = model._meta.model_name
            model_classname = model.__name__

            if hasattr(instance.content_object, model_name):
                model_obj = getattr(instance.content_object, model_name)
                serializer = self.disaster_serializer(model)
                serializer_data = serializer(
                    instance=model_obj,
                    context=self.context
                ).data

                data.update({'content_object': serializer_data})

        return data


class RetrieveActivitySerializer(BaseActivitySerializer):
    pass


class CreateActivitySerializer(BaseActivitySerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta(BaseActivitySerializer.Meta):
        fields = ('user',)


class UpdateActivitySerializer(BaseActivitySerializer):
    pass
