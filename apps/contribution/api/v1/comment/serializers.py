from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.contrib.contenttypes.models import ContentType
from django.urls.base import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import NotFound
from apps.contribution.mixins.activity_mixin import ActivityCreateMixin

Comment = apps.get_registered_model('contribution', 'Comment')
CommentTree = apps.get_registered_model('contribution', 'CommentTree')


class BaseCommentSerializer(serializers.ModelSerializer):
    activity_creator = serializers.CharField(read_only=True)
    is_creator = serializers.BooleanField(read_only=True)
    _links = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get__links(self, instance):
        request = self.context.get('request')
        self_link = reverse('contribution_api:comment-detail',
                            kwargs={'uuid': instance.uuid})
        collection_link = reverse('contribution_api:comment-list')

        return {
            'self': request.build_absolute_uri(self_link),
            'collection': request.build_absolute_uri(collection_link)
        }


class ListCommentSerializer(BaseCommentSerializer):
    class Meta(BaseCommentSerializer.Meta):
        fields = '__all__'


class RetrieveCommentSerializer(BaseCommentSerializer):
    class Meta(BaseCommentSerializer.Meta):
        fields = '__all__'


class CreateCommentSerializer(ActivityCreateMixin, BaseCommentSerializer):
    parent = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Comment.objects.all(),
        required=False
    )

    # for content_type, object_id and content_object
    # commenting target like :report or :disaster
    applied_uuid = serializers.UUIDField()
    applied_model = serializers.CharField()

    class Meta(BaseCommentSerializer.Meta):
        fields = ('parent', 'applied_uuid', 'applied_model', 'description',)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        applied_model = data.pop('applied_model')
        applied_uuid = data.pop('applied_uuid')

        try:
            ct_obj = ContentType.objects.get(model=applied_model)
        except ObjectDoesNotExist:
            raise NotFound(detail=_("Applied model not found"))

        try:
            content_obj = ct_obj.get_object_for_this_type(uuid=applied_uuid)
        except ObjectDoesNotExist:
            raise NotFound(detail=_("Applied object not found"))

        data.update({
            'content_type': ct_obj,
            'object_id': content_obj.id
        })
        return data

    def to_representation(self, instance):
        serializer = RetrieveCommentSerializer(
            instance=instance,
            context=self.context
        )
        return serializer.data

    @transaction.atomic
    def create(self, validated_data):
        parent = validated_data.pop('parent', None)
        instance = self.Meta.model.objects.create(**validated_data)

        # set parent child
        if parent:
            CommentTree.objects.create(parent=parent, child=instance)
        return instance
