from noc.main.report import Column,BooleanColumn
import noc.main.report

class Report(noc.main.report.Report):
    name="cm.config_by_profile"
    title="Configs by profile"
    requires_cursor=True
    columns=[Column("Profile"),Column("Qty")]
    
    def get_queryset(self):
        return self.execute("SELECT profile_name,COUNT(*) FROM cm_config GROUP BY 1 ORDER BY 2 DESC")