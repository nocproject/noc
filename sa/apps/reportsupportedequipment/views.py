# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supported Equipment Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport,TableColumn
from noc.sa.profiles import profile_registry
from noc.sa.protocols.sae_pb2 import TELNET,SSH,HTTP
##
##
##
class Reportreportsupportedequipment(SimpleReport):
    title="Supported Equipment"
    def get_data(self,**kwargs):
        def get_profile_scripts(p):
            return ", ".join(sorted(p.scripts.keys()))
        r=sorted([x for x in profile_registry.classes.items()],lambda x,y:cmp(x[0],y[0]))
        return self.from_dataset(title=self.title,
            columns=[
                "Vendor",
                "OS",
                TableColumn("Telnet",format="bool"),
                TableColumn("SSH",format="bool"),
                TableColumn("HTTP",format="bool"),
                TableColumn("VC Provisioning",format="bool"),
                "Scripts"],
            data=[x.split(".")\
                +[TELNET in c.supported_schemes,SSH in c.supported_schemes,HTTP in c.supported_schemes,
                    "sync_vlans" in c.scripts,get_profile_scripts(c)] for x,c in r],
            enumerate=True)
