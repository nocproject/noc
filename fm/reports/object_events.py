from noc.main.report import Column,BooleanColumn
import noc.main.report

class Report(noc.main.report.Report):
    name="fm.object_events"
    title="Managed Objects Event Summary"
    requires_cursor=True
    columns=[
        Column("Object"),
        Column("Events")]
    
    def get_queryset(self):
        return self.execute("""
            SELECT mo.name,COUNT(*)
            FROM sa_managedobject mo JOIN fm_event e ON (mo.id=e.managed_object_id)
            GROUP BY 1
            ORDER BY 2 DESC""")

