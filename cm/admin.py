from django.contrib import admin
from noc.cm.models import ObjectCategory,Config,DNS,PrefixList

class ObjectCategoryAdmin(admin.ModelAdmin):
    list_display=["name","description"]
    
class ConfigAdmin(admin.ModelAdmin):
    list_display=["repo_path","activator","profile_name","scheme","address","view_link"]
    list_filter=["profile_name","activator"]
    search_fields=["repo_path","address"]

class DNSAdmin(admin.ModelAdmin):
    list_display=["repo_path","view_link"]
    search_fields=["repo_path"]
    
class PrefixListAdmin(admin.ModelAdmin):
    list_display=["repo_path","view_link"]
    search_fields=["repo_path"]

admin.site.register(ObjectCategory, ObjectCategoryAdmin)
admin.site.register(Config,         ConfigAdmin)
admin.site.register(DNS,            DNSAdmin)
admin.site.register(PrefixList,     PrefixListAdmin)
