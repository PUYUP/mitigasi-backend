from django.apps import apps
from django.db import transaction

from rest_framework import serializers

Attachment = apps.get_registered_model('generic', 'Attachment')


class BaseAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'


class RetrieveAttachmentSerializer(BaseAttachmentSerializer):
    class Meta(BaseAttachmentSerializer.Meta):
        pass


class CreateAttachmentSerializer(BaseAttachmentSerializer):
    class Meta(BaseAttachmentSerializer.Meta):
        fields = ('file',)

    def to_representation(self, instance):
        serializer = RetrieveAttachmentSerializer(
            instance=instance,
            context=self.context
        )

        return serializer.data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        instance = super().create(validated_data)

        # create `activity`
        instance.activities.create(user=request.user)
        return instance
