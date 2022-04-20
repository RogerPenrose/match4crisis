from django.contrib import admin

from .models import Newsletter

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'was_sent', 'registration_date', 'last_edited_date')
    list_filter = ('was_sent', 'send_to_organisations', 'send_to_helpers', 'send_to_refugees')
