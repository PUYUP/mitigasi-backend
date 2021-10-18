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


def build_pagination(paginator, serializer):
    result = {
        'count': paginator.count,
        'next': paginator.get_next_link(),
        'previous': paginator.get_previous_link(),
        'results': serializer.data,
    }

    return result
