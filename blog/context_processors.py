from django.conf import settings


def clinic(request):
    """Данные клиники (телефон, адрес, часы) доступны во всех шаблонах как {{ clinic }}."""
    return {'clinic': settings.CLINIC}
