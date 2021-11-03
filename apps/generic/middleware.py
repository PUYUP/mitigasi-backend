from django.apps import apps

Activity = apps.get_registered_model('generic', 'Activity')


class InjectRequestToModelMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # Inject request
        setattr(Activity, 'request', request)

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
