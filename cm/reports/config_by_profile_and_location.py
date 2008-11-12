from noc.main.report import Column,BooleanColumn
import noc.main.report

class Report(noc.main.report.MatrixReport):
    name="cm.config_by_profile_and_location"
    title="Configs by Profile and Location"
    requires_cursor=True
    
    def get_queryset(self):
        return self.execute("SELECT l.name,profile_name,COUNT(*) FROM cm_config c JOIN cm_objectlocation l ON (c.location_id=l.id) GROUP BY 1,2")