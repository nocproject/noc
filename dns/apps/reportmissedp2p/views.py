# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## reportmissedp2p Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport
from noc.ip.models import VRF
##
##
##
class Reportreportmissedp2p(SimpleReport):
    title="Missed Link Addresses"
    def get_data(self,**kwargs):
        vrf_id=VRF.get_global().id
        return self.from_query(title=self.title,
            columns=["Prefix"],
            query="""
            SELECT b.prefix
            FROM ip_ipv4block b
            WHERE vrf_id=%s
                AND (SELECT COUNT(*) FROM ip_ipv4address WHERE vrf_id=%s AND ip<<b.prefix)=0
            ORDER BY prefix
            """,
            params=[vrf_id,vrf_id])
