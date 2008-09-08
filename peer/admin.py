from django.contrib import admin
from noc.peer.models import LIR,AS,ASSet,PeeringPointType,PeeringPoint,PeerGroup,Peer

class LIRAdmin(admin.ModelAdmin): pass

class ASAdmin(admin.ModelAdmin):
    list_display=["asn","description","lir"]
    list_filter=["lir"]
    search_fields=["asn","description"]
        
class ASSetAdmin(admin.ModelAdmin):
    list_display=["name","description","members"]
    search_fields=["name","description","members"]

class PeeringPointTypeAdmin(admin.ModelAdmin):
    list_display=["name"]
        
class PeeringPointAdmin(admin.ModelAdmin):
    list_display=["hostname","router_id","type","communities"]
    list_filter=["type"]
    search_fields=["hostname","router_id"]
        
class PeerGroupAdmin(admin.ModelAdmin):
    list_display=["name","description","communities"]
        
class PeerAdmin(admin.ModelAdmin):
    list_display=["peering_point","local_asn","remote_asn","import_filter","export_filter","local_ip","remote_ip","admin_tt_url","description","communities"]
    search_fields=["remote_asn","description"]
    list_filter=["peering_point"]

admin.site.register(LIR,LIRAdmin)
admin.site.register(AS,ASAdmin)
admin.site.register(ASSet,ASSetAdmin)
#admin.site.register(PeeringPointType,PeeringPointTypeAdmin)
admin.site.register(PeeringPoint,PeeringPointAdmin)
admin.site.register(PeerGroup,PeerGroupAdmin)
admin.site.register(Peer,PeerAdmin)