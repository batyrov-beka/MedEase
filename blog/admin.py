from django.contrib import admin

from .models import ContactRequest


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'short_message', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    list_editable = ('is_processed',)
    search_fields = ('name', 'phone', 'message')

    @admin.display(description='Сообщение')
    def short_message(self, obj):
        return (obj.message[:60] + '…') if len(obj.message) > 60 else obj.message
