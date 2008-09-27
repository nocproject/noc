from django.contrib import admin
from noc.cm.models import ObjectCategory,Object

class ObjectCategoryAdmin(admin.ModelAdmin):
    list_display=["name","description"]
    
class ObjectAdmin(admin.ModelAdmin):
    list_display=["handler_class_name","profile_name","repo_path"]
    search_fields=["repo_path"]
    list_filter=["handler_class_name","profile_name"]
    
admin.site.register(ObjectCategory, ObjectCategoryAdmin)
admin.site.register(Object, ObjectAdmin)
