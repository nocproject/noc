from django.contrib import admin
from django import forms
from noc.cm.models import ObjectCategory,ObjectLocation,ObjectAccess,ObjectNotify,Config,DNS,PrefixList,RPSL
from noc.sa.profiles import profile_registry

class ObjectCategoryAdmin(admin.ModelAdmin):
    list_display=["name","description"]
    
class ObjectLocationAdmin(admin.ModelAdmin):
    list_display=["name","description"]
    
class ObjectAccessAdmin(admin.ModelAdmin):
    list_display=["type","category","location","user"]
    list_filter=["type","category","location"]

class ObjectNotifyAdminForm(forms.ModelForm):
    class Meta:
        model=ObjectNotify
    def clean_emails(self):
        emails=self.cleaned_data["emails"]
        return " ".join(emails.replace(";"," ").replace(","," ").split())
        
class ObjectNotifyAdmin(admin.ModelAdmin):
    form=ObjectNotifyAdminForm
    list_display=["type","category","location","notify_immediately","notify_delayed","emails"]
    list_filter=["type","category","location"]

class ObjectAdmin(admin.ModelAdmin):
    object_class=None
    def has_change_permission(self,request,obj=None):
        if obj:
            return obj.has_access(request.user)
        else:
            return admin.ModelAdmin.has_delete_permission(self,request)
            
    def has_delete_permission(self,request,obj=None):
        return self.has_change_permission(request,obj)
        
    def queryset(self,request):
        return self.object_class.queryset(request.user)
        
    def save_model(self, request, obj, form, change):
        if obj.can_change(request.user,form.cleaned_data["location"],form.cleaned_data["categories"]):
            admin.ModelAdmin.save_model(self,request,obj,form,change)
        else:
            raise "Permission denied"

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
        
class ConfigAdmin(ObjectAdmin):
    form=ConfigAdminForm
    fieldsets=(
        (None,{
            "fields": ("repo_path","location","profile_name","activator")
        }),
        ("Access",{
            "fields": ("scheme","address","port")
        }),
        ("Credentials",{
            "fields": ("user","password","super_password")
        }),
        ("SNMP",{
            "fields": ("trap_source_ip","trap_community")
        }),
        ("Categories", {
            "fields": ("categories",)
        }),
        ("Push/Poll",{
            "classes": ("collapse",),
            "fields":("push_every","next_push","pull_every","next_pull")
        })
    )
    list_display=["repo_path","location","activator","profile_name","scheme","address","last_modified","next_pull","view_link"]
    list_filter=["location","categories","profile_name","activator"]
    search_fields=["repo_path","address"]
    object_class=Config
    
class DNSAdmin(ObjectAdmin):
    list_display=["repo_path","location","last_modified","view_link"]
    list_filter=["location","categories"]
    search_fields=["repo_path"]
    object_class=DNS
    
class PrefixListAdmin(ObjectAdmin):
    list_display=["repo_path","location","last_modified","view_link"]
    list_filter=["location","categories"]
    search_fields=["repo_path"]
    object_class=PrefixList
    
class RPSLAdmin(ObjectAdmin):
    list_display=["repo_path","location","last_modified","view_link"]
    list_filter=["location","categories"]
    search_fields=["repo_path"]
    object_class=RPSL


admin.site.register(ObjectCategory, ObjectCategoryAdmin)
admin.site.register(ObjectLocation, ObjectLocationAdmin)
admin.site.register(ObjectAccess,   ObjectAccessAdmin)
admin.site.register(ObjectNotify,   ObjectNotifyAdmin)
admin.site.register(Config,         ConfigAdmin)
admin.site.register(DNS,            DNSAdmin)
admin.site.register(PrefixList,     PrefixListAdmin)
admin.site.register(RPSL,           RPSLAdmin)

