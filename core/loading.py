from django.apps import apps


def is_model_registered(app_label, model_name):
    """
    Source: https://github.com/django-oscar/django-oscar/blob/master/src/oscar/core/loading.py
    """
    try:
        apps.get_registered_model(app_label, model_name)
    except LookupError:
        return False
    else:
        return True
