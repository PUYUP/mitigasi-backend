from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from .models import DISASTER_CLASSIFY_MODEL_MAPPER


@transaction.atomic
def pre_create_hazard(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = instance.__class__.objects.get(
            id=instance.id
        )
    except ObjectDoesNotExist:
        instance._pre_save_instance = None


@transaction.atomic
def post_create_hazard(sender, instance, created, **kwargs):
    mapper = DISASTER_CLASSIFY_MODEL_MAPPER
    pre_save_instance = instance._pre_save_instance
    classify = instance.classify
    model = mapper.get(classify)

    if pre_save_instance:
        pre_model = mapper.get(pre_save_instance.classify)
        pre_model_objs = pre_model.objects.filter(hazard_id=instance.id)

        if pre_model_objs.exists():
            pre_model_objs.delete()

    # create `flood`
    if model:
        model.objects.get_or_create(hazard=instance)
