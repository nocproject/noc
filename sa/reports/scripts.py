from noc.main.report import Column
import noc.main.report
from noc.sa.models import script_registry

class Report(noc.main.report.Report):
    name="sa.scripts"
    title="Scripts"
    requires_cursor=False
    columns=[Column("Script")]
    
    def get_queryset(self):
        return sorted([[x[0]] for x in script_registry.choices])
