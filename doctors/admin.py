from django.contrib import admin
from django.utils.html import format_html

from .models import Doctor, Specialty, WorkingHours


class WorkingHoursInline(admin.TabularInline):
    model = WorkingHours
    extra = 0
    max_num = 7


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_preview', 'order', 'is_active', 'doctor_count')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    @admin.display(description='Иконка')
    def icon_preview(self, obj):
        return format_html('<code>{}</code>', obj.icon)

    @admin.display(description='Врачей')
    def doctor_count(self, obj):
        return obj.doctors.count()


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'position', 'experience', 'price', 'is_active', 'has_account', 'work_days')
    list_filter = ('specialty', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name', 'position', 'specialty__name')
    autocomplete_fields = ('user',)
    inlines = [WorkingHoursInline]
    fieldsets = (
        (None, {'fields': ('name', 'specialty', 'position', 'photo', 'is_active')}),
        ('О враче', {'fields': ('experience', 'education', 'bio')}),
        ('Приём', {'fields': ('price', 'slot_minutes', 'user')}),
    )

    @admin.display(boolean=True, description='Аккаунт')
    def has_account(self, obj):
        return obj.user_id is not None

    @admin.display(description='Дни приёма')
    def work_days(self, obj):
        return ', '.join(WorkingHours.SHORT[wh.weekday] for wh in obj.working_hours.all()) or '—'
