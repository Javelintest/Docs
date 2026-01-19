from django.contrib import admin
from .models import DocumentTask

@admin.register(DocumentTask)
class DocumentTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_type', 'status', 'created_at', 'finished_at')
    list_filter = ('task_type', 'status', 'created_at')
    search_fields = ('original_filenames', 'error_message')
    readonly_fields = ('created_at', 'finished_at')
