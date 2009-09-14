# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.contrib import admin
from django import forms
from noc.dns.models import DNSServer,DNSZoneProfile,DNSZone,DNSZoneRecordType,DNSZoneRecord

class DNSServerAdmin(admin.ModelAdmin):
    list_display=["name","generator_name","ip","location","description"]
    search_fields=["name","description","ip"]
    list_filter=["generator_name"]
    
class DNSZoneProfileAdmin(admin.ModelAdmin):
    filter_horizontal=["masters","slaves"]

class DNSZoneRecordInlineForm(forms.ModelForm):
    class Meta:
        model=DNSZoneRecord
    def clean_right(self):
        s=[]
        if "left" in self.cleaned_data:
            s+=[self.cleaned_data["left"]]
        s+=[self.cleaned_data["type"].type]
        if "right" in self.cleaned_data:
            s+=[self.cleaned_data["right"]]
        s=" ".join(s)
        if not self.cleaned_data["type"].is_valid(s):
            raise forms.ValidationError("Invalid record")
        return self.cleaned_data["right"]
        
class DNSZoneRecordInline(admin.TabularInline):
    form=DNSZoneRecordInlineForm
    model=DNSZoneRecord
    extra=3
    
class DNSZoneAdmin(admin.ModelAdmin):
    inlines=[DNSZoneRecordInline]
    list_display=["name","description","paid_till","is_auto_generated","profile","serial","distribution","rpsl_link"]
    list_filter=["is_auto_generated","profile"]
    search_fields=["name","description"]
    
class DNSZoneRecordTypeAdmin(admin.ModelAdmin):
    list_display=["type","is_visible","validation"]
    search_fields=["type"]
    list_filter=["is_visible"]

admin.site.register(DNSServer, DNSServerAdmin)
admin.site.register(DNSZoneProfile,DNSZoneProfileAdmin)
admin.site.register(DNSZone,DNSZoneAdmin)
admin.site.register(DNSZoneRecordType,DNSZoneRecordTypeAdmin)
