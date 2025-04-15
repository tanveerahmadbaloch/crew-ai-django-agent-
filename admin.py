from django.contrib import admin
from .models import Content

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'status', 'user')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at',)

