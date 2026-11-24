from django.contrib import admin

from .models import Document
from .forms import DocumentForm


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):

    form = DocumentForm

    list_display = (
        'id',
        'title',
        'created_at',
        'updated_at'
    )

    search_fields = (
        'title',
        'full_text'
    )

    list_filter = (
        'created_at',
        'updated_at'
    )

    readonly_fields = (
        'full_text',
        'created_at',
        'updated_at'
    )

    fields = (
        'title',
        'file',
        'full_text',
        'created_at',
        'updated_at'
    )

    ordering = ('-created_at',)