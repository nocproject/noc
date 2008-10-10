from noc.main.report import Column
import noc.main.report
from noc.sa.profiles import profile_registry

class Report(noc.main.report.Report):
    name="sa.supported_equipment"
    title="Supported Equipment"
    requires_cursor=False
    columns=[Column("Vendor"),Column("OS")]
    
    def get_queryset(self):
        r=[x[0] for x in profile_registry.choices]
        r.sort()
        return [x.split(".") for x in r]