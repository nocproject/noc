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
    name="dns.ns_zones"
    title="Zones at nameservers"
    requires_cursor=True
    columns=[Column("Nameserver"),Column("Master Zones",align="RIGHT"),Column("Slave Zones",align="RIGHT")]
    
    def get_queryset(self):
        return self.execute("""SELECT ns.name,
                                (
                                    SELECT COUNT(*)
                                    FROM dns_dnszoneprofile_masters pm JOIN dns_dnszone z ON (z.profile_id=pm.dnszoneprofile_id)
                                    WHERE pm.dnsserver_id=ns.id AND z.is_auto_generated
                                ) AS masters,
                                (
                                    SELECT COUNT(*)
                                    FROM dns_dnszoneprofile_slaves ps JOIN dns_dnszone z ON (z.profile_id=ps.dnszoneprofile_id)
                                    WHERE ps.dnsserver_id=ns.id AND z.is_auto_generated
                                ) AS slaves
                            FROM dns_dnsserver ns
                            ORDER BY 2 DESC, 1 ASC""")
