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
## Peer application
##
class PeerApplication(ModelApplication):
    model=Peer
    model_admin=PeerAdmin
    menu="Peers"
