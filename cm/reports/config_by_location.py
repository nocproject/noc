from noc.main.report import Column,BooleanColumn
import noc.main.report

class Report(noc.main.report.Report):
    name="cm.config_by_location"
    title="Configs by Location"
    requires_cursor=True
    columns=[Column("Location"),Column("Qty")]
    
    def get_queryset(self):
        return self.execute("SELECT l.name,COUNT(*) FROM cm_config c JOIN cm_objectlocation l ON (c.location_id=l.id) GROUP BY 1 ORDER BY 2 DESC")