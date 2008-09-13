from south.db import db
from noc.peer.models import *

# Values:
#   (QueryType,Command,ArgRequired)
DEFAULT={
    "IOS": [
        ("ipv4:bgp",          "show ip bgp %(query)s"),
        ("advertised-routes", "show ip bgp neighbors %(query)s advertised-routes"),
        ("summary",           "show ip bgp summary"),
        ("ping",              "ping %(query)s"),
        ("trace",             "traceroute %(query)s"),
    ],
    "JUNOS": [
        ("ipv4:bgp",           "show route table inet.0 %(query)s detail"),
        ("advertised-routes" , "show route advertising-protocol bgp %(query)s %(query)s"),
        ("summary",            "show bgp summary"),
        ("ping",               "ping count 5 %(query)s"),
        ("trace",              "traceroute %(query)s as-number-lookup"),
    ]
}

class Migration:
    def forwards(self):
        qtype={}
        for ppt in DEFAULT:
            try:
                p=PeeringPointType.objects.get(name=ppt)
            except PeeringPointType.DoesNotExist:
                p=PeeringPointType(name=ppt)
                p.save()
            for k,v in DEFAULT[ppt]:
                if not k in qtype:
                    q=LGQueryType(name=k)
                    q.save()
                    qtype[k]=q
                q=qtype[k]
                if LGQueryCommand.objects.filter(peering_point_type=p,query_type=q).count()==0:
                    c=LGQueryCommand(peering_point_type=p,query_type=q,command=v)
                    c.save()
    
    def backwards(self):
        "Write your backwards migration here"
