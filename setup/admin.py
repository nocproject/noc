from django.contrib import admin
from noc.setup.models import Settings

class SettingsAdmin(admin.ModelAdmin): pass

admin.site.register(Settings,SettingsAdmin)
