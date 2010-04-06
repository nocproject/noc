# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.contrib import admin
from noc.peer.models import RIR,Person,Maintainer,AS,ASSet,PeeringPoint,PeerGroup,Peer,CommunityType,Community,Organisation
from noc.lib.render import render,render_plain_text

##
## Peer module admin actions
##

##
## Generate RPSL for selected objects
##
def rpsl_for_selected(modeladmin,request,queryset):
    return render_plain_text("\n\n".join([o.rpsl for o in queryset]))
rpsl_for_selected.short_description="RPSL for selected objects"

class RIRAdmin(admin.ModelAdmin): pass

class PersonAdmin(admin.ModelAdmin):
    list_display=["nic_hdl","person","rir"]
    list_filter=["rir"]
    search_fields=["nic_hdl","person"]
    actions=[rpsl_for_selected]

class OrganisationAdmin(admin.ModelAdmin):
    list_display=["organisation","org_name","org_type"]

class MaintainerAdmin(admin.ModelAdmin):
    list_display=["maintainer","description","rir"]
    list_filter=["rir"]
    filter_horizontal=["admins"]
    actions=[rpsl_for_selected]

class ASAdmin(admin.ModelAdmin):
    list_display=["asn","as_name","description","organisation"]
    search_fields=["asn","description"]
    filter_horizontal=["administrative_contacts","tech_contacts","maintainers","routes_maintainers"]
    actions=[rpsl_for_selected,"update_rir_db_for_selected"]
    ##
    ## Update RIR database for selected objects
    ##
    def update_rir_db_for_selected(self,request,queryset):
        u=request.user
        if not u or not u.is_superuser:
            self.message_user(request,"Superuser priveleges required")
            return
        r=[]
        for a in queryset:
            r+=["AS%s %s:\n"%(a.asn,a.as_name)+a.update_rir_db()]
        return render_plain_text("\n\n".join(r))
    update_rir_db_for_selected.short_description="Update RIR DB for selected objects"
    
class CommunityTypeAdmin(admin.ModelAdmin):
    list_display=["name"]
    
class CommunityAdmin(admin.ModelAdmin):
    list_display=["community","type","description"]
    list_filter=["type"]
    search_fields=["community","description"]
        
class ASSetAdmin(admin.ModelAdmin):
    list_display=["name","description","members"]
    search_fields=["name","description","members"]
    actions=[rpsl_for_selected]

class PeeringPointAdmin(admin.ModelAdmin):
    list_display=["hostname","location","local_as","router_id","profile_name","communities"]
    list_filter=["profile_name"]
    search_fields=["hostname","router_id"]
    actions=[rpsl_for_selected]
        
class PeerGroupAdmin(admin.ModelAdmin):
    list_display=["name","description","communities"]
        
class PeerAdmin(admin.ModelAdmin):
    list_display=["peering_point","peer_group","local_asn","remote_asn","status","admin_import_filter","admin_export_filter","admin_local_ip","admin_remote_ip","admin_tt_url","description","communities"]
    search_fields=["remote_asn","description","local_ip","local_backup_ip","remote_ip","remote_backup_ip"]
    list_filter=["peering_point","peer_group","status"]
    actions=["mark_as_planned","mark_as_active","mark_as_shutdown"]
    ##
    ##
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


admin.site.register(RIR,RIRAdmin)
admin.site.register(Person,PersonAdmin)
admin.site.register(Organisation,OrganisationAdmin)
admin.site.register(Maintainer,MaintainerAdmin)
admin.site.register(AS,ASAdmin)
admin.site.register(CommunityType,CommunityTypeAdmin)
admin.site.register(Community,CommunityAdmin)
admin.site.register(ASSet,ASSetAdmin)
admin.site.register(PeeringPoint,PeeringPointAdmin)
admin.site.register(PeerGroup,PeerGroupAdmin)
admin.site.register(Peer,PeerAdmin)
