from django.contrib import admin
from noc.cm.models import Object

class ObjectAdmin(admin.ModelAdmin):
    list_display=["url","profile_name"]
    search_fields=["url"]
    list_filter=["profile_name"]
    
admin.site.register(Object, ObjectAdmin)
