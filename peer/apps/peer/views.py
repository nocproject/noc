# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Peer Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
from django import forms
## NOC modules
from noc.lib.app import ModelApplication
from noc.peer.models import Peer
from noc.lib.tt import admin_tt_url
from noc.lib.validators import *
from noc.lib.ip import IP
##
## Peer form validation
##
class PeerAdminForm(forms.ModelForm):
    class Meta:
        model=Peer
    ##
    ## Clean "Remote ASN" field
    ##
    def clean_remote_asn(self):
        return check_asn(self.cleaned_data["remote_asn"])
    
    ##
    ## Clean addresses
    ##
    def clean_local_ip(self):
        return check_prefix(self.cleaned_data["local_ip"])
    
    def clean_remote_ip(self):
        return check_prefix(self.cleaned_data["remote_ip"])
    
    def clean_local_backup_ip(self):
        if "local_backup_ip" not in self.cleaned_data or not self.cleaned_data["local_backup_ip"]:
            return ""
        return check_prefix(self.cleaned_data["local_backup_ip"])
    
    def clean_remote_backup_ip(self):
        if "remote_backup_ip" not in self.cleaned_data or not self.cleaned_data["remote_backup_ip"]:
            return ""
        return check_prefix(self.cleaned_data["remote_backup_ip"])
    
    def clean(self):
        data=self.cleaned_data
        ## Check no or both backup addresses given
        has_local_backup="local_backup_ip" in data and data["local_backup_ip"]
        has_remote_backup="remote_backup_ip" in data and data["remote_backup_ip"]
        if has_local_backup and not has_remote_backup:
            self._errors["remote_backup_ip"]=self.error_class(["One of backup addresses given. Set peer address"])
        if not has_local_backup and has_remote_backup:
            self._errors["local_backup_ip"]=self.error_class(["One of backup addresses given. Set peer address"])
        ## Check all link addresses belongs to one AFI
        if len(set([IP.prefix(data[x]).afi for x in ["local_ip", "remote_ip", "local_backup_ip", "remote_backup_ip"] if x in data and data[x]]))>1:
            raise forms.ValidationError("All neighboring addresses must have same address family")
        return data
##
## Peer admin
##
class PeerAdmin(admin.ModelAdmin):
    form=PeerAdminForm
    fieldsets=[
        ("Peering", {
            "fields" : ["peering_point", "peer_group", "local_asn", "remote_asn", "status"]
        }),
        ("Link Addresses", {
            "fields": ["local_ip", "local_backup_ip", "remote_ip", "remote_backup_ip"]
        }),
        ("Description", {
            "fields" : ["description", "rpsl_remark"]
        }),
        ("Filters and Limits", {
            "fields": ["import_filter", "export_filter", "import_filter_name", "export_filter_name", "max_prefixes", "communities"]
        }),
        ("Preferences", {
            "fields": ["local_pref", "import_med", "export_med"]
        }),
        ("Tags", {
            "fields": ["tt", "tags"]
        })
    ]
    list_display=["peering_point","peer_group","local_asn","remote_asn","status","admin_import_filter","admin_export_filter","admin_local_ip","admin_remote_ip","admin_tt_url","description","communities"]
    search_fields=["remote_asn","description","local_ip","local_backup_ip","remote_ip","remote_backup_ip"]
    list_filter=["peering_point","peer_group","status"]
    actions=["mark_as_planned","mark_as_active","mark_as_shutdown"]
    ##
    ## Change peer status
    ##
    def set_peer_status(self,request,queryset,status,message):
        count=0
        for p in queryset:
            p.status=status
            p.save()
            count+=1
        if count==1:
            self.message_user(request,"1 peer marked as %s"%message)
        else:
            self.message_user(request,"%d peers marked as %s"%(count,message))
    ##
    ## Mark selected peers as planned
    ##
    def mark_as_planned(self,request,queryset):
        return self.set_peer_status(request,queryset,"P","planned")
    mark_as_planned.short_description="Mark as planned"
    ##
    ## Mark selected peers as planned
    ##
    def mark_as_active(self,request,queryset):
        return self.set_peer_status(request,queryset,"A","active")
    mark_as_active.short_description="Mark as active"
    ##
    ## Mark selected peers as planned
    ##
    def mark_as_shutdown(self,request,queryset):
        return self.set_peer_status(request,queryset,"S","shutdown")
    mark_as_shutdown.short_description="Mark as shutdown"
    ##
    ##
    ##
    def admin_tt_url(self,obj):
        return admin_tt_url(obj)
    admin_tt_url.short_description="TT"
    admin_tt_url.allow_tags=True
    ##
    ##
    ##
    def admin_import_filter(self,obj):
        r=[]
        if obj.import_filter:
            r+=[obj.import_filter]
        if obj.import_filter_name:
            r+=["(%s)"%obj.import_filter_name]
        return "<BR/>".join(r)
    admin_import_filter.short_description="Import Filter"
    admin_import_filter.allow_tags=True
    ##
    ##
    ##
    def admin_export_filter(self,obj):
        r=[]
        if obj.export_filter:
            r+=[obj.export_filter]
        if obj.export_filter_name:
            r+=["(%s)"%obj.export_filter_name]
        return "<BR/>".join(r)
    admin_export_filter.short_description="Export Filter"
    admin_export_filter.allow_tags=True
    ##
    ##
    ##
    def admin_local_ip(self,obj):
        r=[obj.local_ip]
        if obj.local_backup_ip:
            r+=[obj.local_backup_ip]
        return "<BR/>".join(r)
    admin_local_ip.short_description="Local Address"
    admin_local_ip.allow_tags=True
    ##
    ##
    ##
    def admin_remote_ip(self,obj):
        r=[obj.remote_ip]
        if obj.remote_backup_ip:
            r+=[obj.remote_backup_ip]
        return "<BR/>".join(r)
    admin_remote_ip.short_description="Remote Address"
    admin_remote_ip.allow_tags=True
##
## Peer application
##
class PeerApplication(ModelApplication):
    model=Peer
    model_admin=PeerAdmin
    menu="Peers"
