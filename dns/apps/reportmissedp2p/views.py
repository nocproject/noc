# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## reportmissedp2p Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Django Modules
from django.utils.translation import ugettext_lazy as _
# NOC Modules
from noc.lib.app.simplereport import SimpleReport
from noc.ip.models import VRF
##
##
##
class Reportreportmissedp2p(SimpleReport):
    title=_("Missed Link Addresses")
    def get_data(self,**kwargs):
        vrf_id=VRF.get_global().id
        return self.from_query(title=self.title,
            columns=[_("Prefix")],
            query="""
            SELECT prefix
            FROM   ip_prefix p
            WHERE 
                vrf_id=%s
                AND afi='4'
                AND masklen(prefix)=30
                AND NOT EXISTS (SELECT * FROM ip_address WHERE vrf_id=%s AND afi='4' AND prefix=p.prefix)
            ORDER BY prefix
            """,
            params=[vrf_id,vrf_id],
            enumerate=True)
    
