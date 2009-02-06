# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.peer.models import *

# Values:
#   (QueryType,Command,ArgRequired)
DEFAULT={
    "Cisco.IOS": [
        ("ipv4:bgp",          "show ip bgp %(query)s"),
        ("advertised-routes", "show ip bgp neighbors %(query)s advertised-routes"),
        ("summary",           "show ip bgp summary"),
        ("ping",              "ping %(query)s"),
        ("trace",             "traceroute %(query)s"),
    ],
    "Juniper.JUNOS": [
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
            if db.execute("SELECT COUNT(*) FROM peer_peeringpointtype WHERE name=%s",[ppt])[0][0]==0:
                db.execute("INSERT INTO peer_peeringpointtype(name) VALUES(%s)",[ppt])
            ppt_id=db.execute("SELECT id FROM peer_peeringpointtype WHERE name=%s",[ppt])[0][0]
            for k,v in DEFAULT[ppt]:
                if not k in qtype:
                    db.execute("INSERT INTO peer_lgquerytype(name) VALUES(%s)",[k])
                    qtype[k]=db.execute("SELECT id FROM peer_lgquerytype WHERE name=%s",[k])[0][0]
                q=qtype[k]
                if db.execute("SELECT COUNT(*) FROM peer_lgquerycommand WHERE peering_point_type_id=%s AND query_type_id=%s",[ppt_id,q])[0][0]==0:
                    db.execute("INSERT INTO peer_lgquerycommand(peering_point_type_id,query_type_id,command) VALUES(%s,%s,%s)",[ppt_id,q,v])
    
    def backwards(self):
        "Write your backwards migration here"
