# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Missed Reverse Zones Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django Modules
from django.utils.translation import ugettext_lazy as _
## NOC Modules
from noc.lib.app.simplereport import SimpleReport,TableColumn
from noc.ip.models import VRF
##
##
##
class Reportreportmissedreverse(SimpleReport):
    title=_("Missed Reverse Zones")
    def get_data(self,**kwargs):
        def reverse_format(p):
            n,m=p.split("/")
            n=n.split(".")[:-1]
            n.reverse()
            return "%s.%s.%s.in-addr.arpa"%(n[0],n[1],n[2])
        vrf_id=VRF.get_global().id
        return self.from_query(title=self.title,
            columns=[
                "Prefix",
                TableColumn("Zone",format=reverse_format)
                ],
            query="""
                SELECT prefix,prefix
                FROM ip_prefix
                WHERE vrf_id=%s
                    AND masklen(prefix)=24
                    AND regexp_replace(host(prefix),E'([0-9]+)\\\\.([0-9]+)\\\\.([0-9]+)\\\\.([0-9]+)',E'\\\\3.\\\\2.\\\\1.in-addr.arpa')
                        NOT IN (SELECT name FROM dns_dnszone WHERE name LIKE '%%.in-addr.arpa')
                ORDER BY 1
            """,
            params=[vrf_id],
            enumerate=True)
