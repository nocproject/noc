# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Peer Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.peer.models import Peer
from noc.lib.tt import admin_tt_url
##
## Peer admin
##
class PeerAdmin(admin.ModelAdmin):
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
