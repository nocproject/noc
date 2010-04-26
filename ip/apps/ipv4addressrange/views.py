# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IPv4Range Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django import forms
from noc.lib.app import ModelApplication
from noc.ip.models import IPv4AddressRange
import re

rx_range_op=re.compile(r"^([/+])(\d+)$")
##
## IPv4Range Field with validation
##
class IPv4RangeField(forms.Field):
    def clean(self,value):
        if not is_ipv4(value) and not rx_range_op.match(value):
            raise ValidationError("Invalid  IPv4 Address")
        return value
##
## IPv4 Range admin form
##
class IPv4AddressRangeAdminForm(forms.ModelForm):
    class Meta:
        model=IPv4AddressRange
    to_ip=IPv4RangeField()
    def clean(self):
        try:
            instance=self.instance
        except:
            instance=None
        for k in ["vrf","from_ip","to_ip"]:
            if k not in self.cleaned_data:
                return self.cleaned_data
        vrf=self.cleaned_data["vrf"]
        from_ip=self.cleaned_data["from_ip"]
        to_ip=self.cleaned_data["to_ip"]
        match=rx_range_op.match(to_ip)
        if match:
            # Process +d and /d forms
            op=match.group(1)
            v=int(match.group(2))
            if op=="+":
                to_ip=int_to_address(address_to_int(from_ip)+v-1)
            elif op=="/":
                to_ip=broadcast(from_ip+to_ip)
            self.cleaned_data["to_ip"]=to_ip
        if cmp_ip(from_ip,to_ip)>0:
            raise forms.ValidationError("'To IP' must be not less than 'From IP'")
        # Check for lock status
        if self.cleaned_data["is_locked"]==False and self.cleaned_data["fqdn_action"]!="N":
            raise forms.ValidationError("Need to lock range for FQDN Action")
        if self.cleaned_data["fqdn_action"] in ["G","D"] and not self.cleaned_data["fqdn_action_parameter"]:
            raise forms.ValidationError("FQDN Action Parameter required")
        # Check for overlapped ranges
        ro=list(IPv4AddressRange.get_range_overlap(vrf,from_ip,to_ip,instance)[:10])
        if ro:
            raise forms.ValidationError("Range overlaps with %s"%",".join([unicode(r) for r in ro]))
        # Check for overlapped blocks
        bo=list(IPv4AddressRange.get_block_overlap(vrf,from_ip,to_ip)[:10])
        if bo:
            raise forms.ValidationError("Range overlaps with blocks %s"%",".join([unicode(r) for r in bo]))
        return super(IPv4AddressRangeAdminForm,self).clean()
##
## IPv4 Range Admin
##
class IPv4AddressRangeAdmin(admin.ModelAdmin):
    form=IPv4AddressRangeAdminForm
    list_display=["name","vrf","from_ip","to_ip","is_locked","fqdn_action","fqdn_action_parameter"]
    list_filter=["is_locked","vrf"]
    search_fields=["name"]
##
## IPv4Range application
##
class IPv4AddressRangeApplication(ModelApplication):
    model=IPv4AddressRange
    model_admin=IPv4AddressRangeAdmin
    menu="Setup | IPv4 Address Ranges"
