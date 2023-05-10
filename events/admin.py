from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.Event)
class UserEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'start_at', 'end_at', 'created_by', 'updated_by', 'invitation_sent']
    # list_filter = ['created_at', 'updated_at']
