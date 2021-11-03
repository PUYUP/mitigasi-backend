from .models import HAZARD_CLASSIFY_MODEL_MAPPER


def create_hazard(sender, instance, created, **kwargs):
    if created:
        # create hazard
        classify = instance.classify
        model = HAZARD_CLASSIFY_MODEL_MAPPER.get(classify)

        if model:
            model.objects.create(hazard=instance)
