from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Медицинская карта'


admin.site.unregister(User)


@admin.register(User)
class MedUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff')

    @admin.display(description='Телефон')
    def phone(self, obj):
        return getattr(getattr(obj, 'profile', None), 'phone', '')
