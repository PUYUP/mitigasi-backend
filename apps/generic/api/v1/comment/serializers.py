from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.urls.base import reverse

from rest_framework import serializers
from rest_framework.exceptions import NotFound

Comment = apps.get_registered_model('generic', 'Comment')
CommentTree = apps.get_registered_model('generic', 'CommentTree')


class BaseCommentSerializer(serializers.ModelSerializer):
    authored = serializers.BooleanField(read_only=True)
    activity_author = serializers.CharField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    _links = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get__links(self, instance):
        request = self.context.get('request')
        self_link = reverse('generic_api:comment-detail',
                            kwargs={'uuid': instance.uuid})
        collection_link = reverse('generic_api:comment-list')

        return {
            'self': request.build_absolute_uri(self_link),
            'collection': request.build_absolute_uri(collection_link)
        }


class ParentCommentSerializer(BaseCommentSerializer):
    class Meta(BaseCommentSerializer.Meta):
        pass


class RetrieveCommentSerializer(BaseCommentSerializer):
    parent = ParentCommentSerializer()

    class Meta(BaseCommentSerializer.Meta):
        pass


class ListCommentSerializer(BaseCommentSerializer):
    parent = ParentCommentSerializer()

    class Meta(BaseCommentSerializer.Meta):
        pass


class CreateCommentSerializer(BaseCommentSerializer):
    parent = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Comment.objects.all(),
        required=False
    )

    class Meta(BaseCommentSerializer.Meta):
        fields = ('description', 'content_type', 'object_id', 'parent',)

    def to_internal_value(self, data):
        object_id = data.get('object_id', None)
        content_type = data.get('content_type', None)
        content_type_param = dict()
        content_type_objs = ContentType.objects.filter(model=content_type)

        for ct in content_type_objs:
            model = ct.model_class()
            if model and hasattr(model, 'comments'):
                content_type_param.update({
                    'model': model._meta.model_name,
                    'app_label': model._meta.app_label,
                })

                break

        if content_type_param:
            try:
                content_type_obj = ContentType.objects.get(
                    **content_type_param)
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
        serializer = RetrieveCommentSerializer(
            instance=instance,
            context=self.context
        )
        data.update(serializer.data)

        return data

    @transaction.atomic
    def create(self, validated_data):
        parent = validated_data.pop('parent', None)
        request = self.context.get('request')
        instance = super().create(validated_data)

        # set parent child
        if parent:
            CommentTree.objects.create(parent=parent, child=instance)

        # create `activity`
        instance.activities.create(user=request.user)
        return instance


class UpdateCommentSerializer(BaseCommentSerializer):
    class Meta(BaseCommentSerializer.Meta):
        fields = ('description',)

    def to_representation(self, instance):
        serializer = RetrieveCommentSerializer(
            instance=instance,
            context=self.context
        )

        return serializer.data
