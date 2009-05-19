# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column,BooleanColumn
import noc.main.report
from noc.sa.profiles import profile_registry
from noc.sa.protocols.sae_pb2 import TELNET,SSH,HTTP

class Report(noc.main.report.Report):
    name="sa.supported_equipment"
    title="Supported Equipment"
    requires_cursor=False
    columns=[Column("Vendor"),Column("OS"),BooleanColumn("Telnet"),BooleanColumn("SSH"),BooleanColumn("HTTP"),
        BooleanColumn("Super command"),Column("Scripts")]
    
    def get_queryset(self):
        def get_profile_scripts(p):
            return ", ".join(p.scripts.keys())
        r=[x for x in profile_registry.classes.items()]
        r.sort(lambda x,y:cmp(x[0],y[0]))
        return [x.split(".")\
            +[TELNET in c.supported_schemes,SSH in c.supported_schemes,HTTP in c.supported_schemes,c.command_super,
                get_profile_scripts(c)] for x,c in r]
