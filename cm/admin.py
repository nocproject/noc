from django.contrib import admin
from noc.cm.models import ObjectCategory,Object

class ObjectCategoryAdmin(admin.ModelAdmin):
    list_display=["name","description"]
    
class ObjectAdmin(admin.ModelAdmin):
    list_display=["url","profile_name"]
    search_fields=["url"]
    list_filter=["profile_name"]
    
admin.site.register(ObjectCategory, ObjectCategoryAdmin)
admin.site.register(Object, ObjectAdmin)
