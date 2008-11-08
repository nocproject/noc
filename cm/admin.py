from django.contrib import admin
from django import forms
from noc.cm.models import ObjectCategory,Config,DNS,PrefixList,RPSL
from noc.sa.profiles import profile_registry

class ObjectCategoryAdmin(admin.ModelAdmin):
    list_display=["name","description"]
    
class ConfigAdminForm(forms.ModelForm):
    class Meta:
        model=Config
    def clean_scheme(self):
        if "profile_name" not in self.cleaned_data:
            return self.cleaned_data["scheme"]
        profile=profile_registry[self.cleaned_data["profile_name"]]
        if self.cleaned_data["scheme"] not in profile.supported_schemes:
            raise forms.ValidationError("Selected scheme is not supported for profile '%s'"%self.cleaned_data["profile_name"])
        return self.cleaned_data["scheme"]
        
class ConfigAdmin(admin.ModelAdmin):
    form=ConfigAdminForm
    list_display=["repo_path","activator","profile_name","scheme","address","last_modified","pull_every","last_pull","next_pull","view_link"]
    list_filter=["categories","profile_name","activator"]
    search_fields=["repo_path","address"]

class DNSAdmin(admin.ModelAdmin):
    list_display=["repo_path","last_modified","view_link"]
    list_filter=["categories"]
    search_fields=["repo_path"]
    
class PrefixListAdmin(admin.ModelAdmin):
    list_display=["repo_path","last_modified","view_link"]
    list_filter=["categories"]
    search_fields=["repo_path"]
    
class RPSLAdmin(admin.ModelAdmin):
    list_display=["repo_path","last_modified","view_link"]
    list_filter=["categories"]
    search_fields=["repo_path"]

admin.site.register(ObjectCategory, ObjectCategoryAdmin)
admin.site.register(Config,         ConfigAdmin)
admin.site.register(DNS,            DNSAdmin)
admin.site.register(PrefixList,     PrefixListAdmin)
admin.site.register(RPSL,           RPSLAdmin)

