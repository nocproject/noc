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
        BooleanColumn("Super command"),BooleanColumn("SNMP Config Trap"),BooleanColumn("Syslog Config"),BooleanColumn("LG Hilight"),
        Column("Scripts")]
    
    def get_queryset(self):
        def get_profile_scripts(p):
            print p,p.scripts
            return ", ".join(p.scripts.keys())
        r=[x for x in profile_registry.classes.items()]
        r.sort(lambda x,y:cmp(x[0],y[0]))
        return [x.split(".")\
            +[TELNET in c.supported_schemes,SSH in c.supported_schemes,HTTP in c.supported_schemes,c.command_super,c.oid_trap_config_changed,c.syslog_config_changed]\
            +[c.pattern_lg_as_path_list is not None or c.pattern_lg_best_path is not None,get_profile_scripts(c)] for x,c in r]
