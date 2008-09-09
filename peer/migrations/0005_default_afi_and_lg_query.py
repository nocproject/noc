
from south.db import db
from noc.peer.models import *

DEFAULT={
    "Cisco": {
        "ipv4" : {
            "bgp"               : "show ip bgp %(query)s",
            "advertised-routes" : "show ip bgp neighbors %(query)s advertised-routes",
            "summary"           : "show ip bgp summary",
            "ping"              : "ping %(query)s",
            "trace"             : "traceroute %(query)s",
        },
        "ipv6" : {
            "bgp"               : "show bgp ipv6 %(query)s",
            "advertised-routes" : "show bgp ipv6 neighbors %(query)s advertised-routes",
            "summary"           : "show bgp ipv6 summary",
            "ping"              : "ping ipv6 %(query)s",
            "trace"             : "traceroute ipv6 %(query)s",
        }
    },
    "Juniper": {
        "ipv4" : {
            "bgp"               : "show bgp %(query)s",
            "advertised-routes" : "show route advertising-protocol bgp %(query)s %(query)s",
            "summary"           : "show bgp summary",
            "ping"              : "ping count 5 %(query)s",
            "trace"             : "traceroute %(query)s as-number-lookup",
        },
        "ipv6" : {
            "bgp"               : "show bgp %(query)s",
            "advertised-routes" : "show route advertising-protocol bgp %(query)s %(query)s",
            "summary"           : "show bgp summary",
            "ping"              : "ping count 5 %(query)s",
            "trace"             : "traceroute %(query)s",
        }
    }
}

class Migration:
    def forwards(self):
        afis={}
        for pp_type,values in DEFAULT.items():
            ppt=PeeringPointType.objects.get(name=pp_type)
            for afi,queries in values.items():
                if afi not in afis:
                    try:
                        a=AFI.objects.get(afi=afi)
                    except:
                        a=AFI(afi=afi)
                        a.save()
                    afis[afi]=a
                for query,command in queries.items():
                    if LGQuery.objects.filter(peering_point_type=ppt,afi=afis[afi],query=query).count()==0:
                        q=LGQuery(peering_point_type=ppt,afi=afis[afi],query=query,command=command)
                        q.save()
    
    def backwards(self):
        afis={}
        for pp_type,values in DEFAULT.items():
            try:
                ppt=PeeringPointType.objects.get(name=pp_type)
            except:
                continue
            for afi,queries in values.items():
                if afi not in afis:
                    try:
                        afis[afi]=AFI.objects.get(afi=afi)
                    except:
                        continue
                for query,command in queries.items():
                    r=list(LGQuery.objects.filter(peering_point_type=ppt,afi=afis[afi],query=query))
                    if len(r)==1 and r[0].command==command:
                        r[0].delete()
        for afi in afis.values():
            afi.delete()
