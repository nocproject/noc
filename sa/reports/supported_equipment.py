from noc.main.report import Column,BooleanColumn
import noc.main.report
from noc.sa.profiles import profile_registry
from noc.sa.protocols.sae_pb2 import TELNET,SSH,HTTP

class Report(noc.main.report.Report):
    name="sa.supported_equipment"
    title="Supported Equipment"
    requires_cursor=False
    columns=[Column("Vendor"),Column("OS"),BooleanColumn("Telnet"),BooleanColumn("SSH"),BooleanColumn("HTTP"),
        BooleanColumn("Super command"),BooleanColumn("SNMP Config Trap"),BooleanColumn("LG Hilight")]
    
    def get_queryset(self):
        r=[x for x in profile_registry.classes.items()]
        r.sort(lambda x,y:cmp(x[0],y[0]))
        return [x.split(".")\
            +[TELNET in c.supported_schemes,SSH in c.supported_schemes,HTTP in c.supported_schemes,c.command_super,c.oid_trap_config_changed]\
            +[c.pattern_lg_as_path_list is not None or c.pattern_lg_best_path is not None] for x,c in r]