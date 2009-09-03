# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column
import noc.main.report

def prefix_to_zone(p):
    n,m=p.split("/")
    n=n.split(".")[:-1]
    n.reverse()
    return "%s.%s.%s.in-addr.arpa"%(n[2],n[1],n[0])

class Report(noc.main.report.Report):
    name="dns.missed_reverse_zones"
    title="Missed Reverse Zones"
    requires_cursor=True
    columns=[Column("Prefix",format=lambda x:"<A HREF='/ip/%s/'>%s</A>"%(x,x.split("/",1)[0])),
             Column('Zone', format=prefix_to_zone)]
    
    def get_queryset(self):
        vrf_id=self.execute("SELECT id FROM ip_vrf WHERE rd='0:0'")[0][0]
        return self.execute("""
            SELECT prefix,prefix
            FROM ip_ipv4block
            WHERE vrf_id=%s
                AND masklen(prefix)=24
                AND regexp_replace(host(prefix),'([0-9]+)\\.([0-9]+)\\.([0-9]+)\\.([0-9]+)','\\3.\\2.\\1.in-addr.arpa')
                    NOT IN (SELECT name FROM dns_dnszone)""",[vrf_id])
