# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Duplicated FQDNs Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport
from noc.ip.models import VRF
##
##
##
class Reportreportduplicatedfqdns(SimpleReport):
    title="Duplicated FQDNs"
    def get_data(self,**kwargs):
        vrf_id=VRF.get_global().id
        return self.from_query(title=self.title,
            columns=["FQDN","N","Addresses"],
            query="""
            SELECT fqdn,COUNT(*),
                array_to_string(ARRAY(SELECT address FROM ip_address WHERE fqdn=a.fqdn AND vrf_id=%s ORDER BY address),', ')
            FROM ip_address a
            WHERE vrf_id=%s
            GROUP BY 1
            HAVING COUNT(*)>1
            ORDER BY 2 DESC""",
            params=[vrf_id,vrf_id])
