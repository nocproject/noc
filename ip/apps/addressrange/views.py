# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AddressRange Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Django Modules
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django import forms
# NOC Modules
from noc.lib.app import ModelApplication
from noc.ip.models import AddressRange
from noc.lib.ip import *
from noc.lib.validators import *
##
## Address range form
##
class AddressRangeAdminForm(forms.ModelForm):
    class Meta:
        model=AddressRange
    
    def clean(self):
        afi=self.cleaned_data["afi"]
        from_address=self.cleaned_data["from_address"]
        to_address=self.cleaned_data["to_address"]
        # Check AFI
        address_validator=is_ipv4 if afi=="4" else is_ipv6
        if not address_validator(from_address):
            self._errors["from_address"]=self.error_class([_("Invalid IPv%(afi)s address")%{"afi":afi}])
        if not address_validator(to_address):
            self._errors["to_address"]=self.error_class([_("Invalid IPv%(afi)s address")%{"afi":afi}])
        # Check from address not greater than to address
        if IP.prefix(from_address)>IP.prefix(to_address):
            self._errors["to_address"]=self.error_class([_("Must be greater or equal than 'From Address'")])
        # Check for valid "action" combination
        if "fqdn_template" in self.cleaned_data and self.cleaned_data["fqdn_template"] and self.cleaned_data["action"]!="G":
            self._errors["fqdn_template"]=self.error_class([_("Must be clean for selected 'Action'")])
        if "reverse_nses" in self.cleaned_data and self.cleaned_data["reverse_nses"] and self.cleaned_data["action"]!="D":
            self._errors["reverse_nses"]=self.error_class([_("Must be clean for selected 'Action'")])
        # Set range as locked for "G" and "D" actions
        if self.cleaned_data["action"]!="N":
            self.cleaned_data["is_locked"]=True
        # @todo: check FQDN template
        # Check reverse_nses is a list of FQDNs or IPs
        if "reverse_nses" in self.cleaned_data and self.cleaned_data["reverse_nses"]:
            reverse_nses=self.cleaned_data["reverse_nses"]
            for ns in reverse_nses.split(","):
                ns=ns.strip()
                if not is_ipv4(ns) and not is_ipv6(ns) and not is_fqdn(ns):
                    self._errors["reverse_nses"]=self.error_class([_("Invalid nameserver")])
                    break
        # Check no locked range overlaps another locked range
        if self.cleaned_data["is_locked"]:
            r=[r for r in AddressRange.get_overlapping_ranges(self.cleaned_data["vrf"],self.cleaned_data["afi"],
                self.cleaned_data["from_address"],self.cleaned_data["to_address"]) if r.is_locked==True]
            if r:
                raise forms.ValidationError("Locked range overlaps with ahother locked range: %s"%unicode(r[0]))
        return self.cleaned_data
    

##
## AddressRange admin
##
class AddressRangeAdmin(admin.ModelAdmin):
    form=AddressRangeAdminForm
    list_display=["name","is_active","vrf","afi","from_address","to_address","is_locked","action","description"]
    list_filter=["is_active","vrf","afi","action","is_locked"]
    search_fields=["name","description"]

##
## AddressRange application
##
class AddressRangeApplication(ModelApplication):
    model=AddressRange
    model_admin=AddressRangeAdmin
    menu="Setup | Address Ranges"
