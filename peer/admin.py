# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.contrib import admin
from noc.peer.models import RIR,Person,Maintainer,AS,ASSet,PeeringPoint,PeerGroup,Peer,CommunityType,Community

class RIRAdmin(admin.ModelAdmin): pass

class PersonAdmin(admin.ModelAdmin):
    list_display=["nic_hdl","person","rir","rpsl_link"]
    list_filter=["rir"]
    search_fields=["nic_hdl","person"]

class MaintainerAdmin(admin.ModelAdmin):
    list_display=["maintainer","description","rir","rpsl_link"]
    list_filter=["rir"]

class ASAdmin(admin.ModelAdmin):
    list_display=["asn","description","maintainer","rpsl_link"]
    list_filter=["maintainer"]
    search_fields=["asn","description"]
    
class CommunityTypeAdmin(admin.ModelAdmin):
    list_display=["name"]
    
class CommunityAdmin(admin.ModelAdmin):
    list_display=["community","type","description"]
    list_filter=["type"]
    search_fields=["community","description"]
        
class ASSetAdmin(admin.ModelAdmin):
    list_display=["name","description","members","rpsl_link"]
    search_fields=["name","description","members"]

class PeeringPointAdmin(admin.ModelAdmin):
    list_display=["hostname","location","local_as","router_id","profile_name","communities","rpsl_link"]
    list_filter=["profile_name"]
    search_fields=["hostname","router_id"]
        
class PeerGroupAdmin(admin.ModelAdmin):
    list_display=["name","description","communities"]
        
class PeerAdmin(admin.ModelAdmin):
    list_display=["peering_point","local_asn","remote_asn","admin_import_filter","admin_export_filter","local_ip","masklen","remote_ip","admin_tt_url","description","communities"]
    search_fields=["remote_asn","description"]
    list_filter=["peering_point"]

admin.site.register(RIR,RIRAdmin)
admin.site.register(Person,PersonAdmin)
admin.site.register(Maintainer,MaintainerAdmin)
admin.site.register(AS,ASAdmin)
admin.site.register(CommunityType,CommunityTypeAdmin)
admin.site.register(Community,CommunityAdmin)
admin.site.register(ASSet,ASSetAdmin)
admin.site.register(PeeringPoint,PeeringPointAdmin)
admin.site.register(PeerGroup,PeerGroupAdmin)
admin.site.register(Peer,PeerAdmin)
