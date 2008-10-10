from noc.main.report import Column,BooleanColumn
import noc.main.report
from noc.sa.profiles import profile_registry

class Report(noc.main.report.Report):
    name="sa.supported_equipment"
    title="Supported Equipment"
    requires_cursor=False
    columns=[Column("Vendor"),Column("OS"),BooleanColumn("LG Hilight")]
    
    def get_queryset(self):
        r=[x for x in profile_registry.classes.items()]
        r.sort(lambda x,y:cmp(x[0],y[0]))
        return [x.split(".")+[c.pattern_lg_as_path_list is not None or c.pattern_lg_best_path is not None] for x,c in r]