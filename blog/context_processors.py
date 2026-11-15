from django.conf import settings


def clinic(request):
    return {'clinic': settings.CLINIC}
