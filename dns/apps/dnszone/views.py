# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNSZone Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django import forms
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.dns.models import DNSZone,DNSZoneRecord
##
## Validation form for RR inlines
##
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
##
## RR inline form
##
class DNSZoneRecordInline(admin.TabularInline):
    form=DNSZoneRecordInlineForm
    model=DNSZoneRecord
    extra=3
##
## DNSZone admin
##
class DNSZoneAdmin(admin.ModelAdmin):
    inlines=[DNSZoneRecordInline]
    list_display=["name","description","paid_till","is_auto_generated","profile","serial","distribution"]
    list_filter=["is_auto_generated","profile"]
    search_fields=["name","description"]
    actions=["rpsl_for_selected"]
    ##
    ## Generate RPSL for selected objects
    ##
    def rpsl_for_selected(self,request,queryset):
        return self.app.render_plain_text("\n\n".join([o.rpsl for o in queryset]))
    rpsl_for_selected.short_description="RPSL for selected objects"
##
## DNSZone application
##
class DNSZoneApplication(ModelApplication):
    model=DNSZone
    model_admin=DNSZoneAdmin
    menu="Zones"
