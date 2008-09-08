##
##
##
from django.contrib import admin
from noc.dns.models import DNSZoneProfile,DNSZone,DNSZoneRecordType,DNSZoneRecord

class DNSZoneProfileAdmin(admin.ModelAdmin):
    pass

class DNSZoneRecordInline(admin.TabularInline):
    model=DNSZoneRecord
    extra=3
    
class DNSZoneAdmin(admin.ModelAdmin):
    inlines=[DNSZoneRecordInline]
    list_display=["name","description","is_auto_generated"]
    list_filter=["is_auto_generated"]
    search_fields=["name","description"]
    
class DNSZoneRecordTypeAdmin(admin.ModelAdmin):
    list_display=["type"]
    search_fields=["type"]

admin.site.register(DNSZoneProfile,DNSZoneProfileAdmin)
admin.site.register(DNSZone,DNSZoneAdmin)
admin.site.register(DNSZoneRecordType,DNSZoneRecordTypeAdmin)
