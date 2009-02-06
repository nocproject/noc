# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""

from noc.main.report import Column
import noc.main.report

class Report(noc.main.report.Report):
    name="dns.duplicated_fqdns"
    title="Duplicated FQDNs"
    requires_cursor=True
    columns=[Column("FQDN"),Column("IPs")]
    
    def get_queryset(self):
        vrf_id=self.execute("SELECT id FROM ip_vrf WHERE rd='0:0'")[0][0]
        r=[]
        for fqdn,c in self.execute("""
                SELECT fqdn,COUNT(*)
                FROM ip_ipv4address
                WHERE vrf_id=%s
                GROUP BY 1
                HAVING COUNT(*)>1
                ORDER BY 2 DESC""",[vrf_id]):
            ips=", ".join([x[0] for x in self.execute("SELECT ip FROM ip_ipv4address WHERE fqdn=%s and vrf_id=%s",[fqdn,vrf_id])])
            r+=[[fqdn,ips]]
        return r
