from django.db import migrations


def merge_names(apps, schema_editor):
    """Раньше имя и фамилия хранились в двух полях (patient и patient_name) — объединяем в одно ФИО."""
    Appointment = apps.get_model('appointments', 'Appointment')
    for a in Appointment.objects.all():
        parts = [p.strip() for p in (a.patient or '', a.patient_name or '') if p and p.strip()]
        a.patient_name = ' '.join(parts) or a.user.get_full_name() or a.user.username
        a.save(update_fields=['patient_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0003_appointment_patient'),
    ]

    operations = [
        migrations.RunPython(merge_names, migrations.RunPython.noop),
        migrations.RemoveField('appointment', 'patient'),
    ]
