from django.conf import settings

def debug_status(request):
    return {'debug': settings.DEBUG}
