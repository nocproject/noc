# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supported Nameservers Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport
from noc.dns.generators import generator_registry
##
##
##
class Reportreportsupportedns(SimpleReport):
    title="Supported Nameservers"
    def get_data(self,**kwargs):
        r=[x[0] for x in generator_registry.choices]
        return self.from_dataset(title=self.title,columns=["Type"],data=[[x] for x in sorted(r)],enumerate=1)
