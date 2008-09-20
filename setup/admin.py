from django.contrib import admin
from noc.setup.models import Settings

class SettingsAdmin(admin.ModelAdmin):
    list_display=["key","value","default"]
    search_fields=["key","value"]

admin.site.register(Settings,SettingsAdmin)
