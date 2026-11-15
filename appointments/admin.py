from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'patient_name', 'phone', 'doctor', 'status', 'created_at')
    list_filter = ('status', 'doctor__specialty', 'doctor', 'date')
    search_fields = ('patient_name', 'phone', 'user__username', 'user__email', 'doctor__name')
    date_hierarchy = 'date'
    list_select_related = ('doctor',)
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_confirmed', 'mark_cancelled']
    fieldsets = (
        ('Пациент', {'fields': ('user', 'patient_name', 'phone', 'reason')}),
        ('Приём', {'fields': ('doctor', 'date', 'time', 'status')}),
        ('Заключение', {'fields': ('doctor_notes',)}),
        ('Служебное', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.action(description='Подтвердить выбранные записи')
    def mark_confirmed(self, request, queryset):
        n = queryset.filter(status=Appointment.Status.PENDING).update(status=Appointment.Status.CONFIRMED)
        self.message_user(request, f'Подтверждено записей: {n}')

    @admin.action(description='Отменить выбранные записи')
    def mark_cancelled(self, request, queryset):
        n = queryset.filter(status__in=Appointment.ACTIVE_STATUSES).update(status=Appointment.Status.CANCELLED)
        self.message_user(request, f'Отменено записей: {n}')
