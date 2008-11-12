from noc.main.report import Column,BooleanColumn
import noc.main.report

class Report(noc.main.report.Report):
    name="cm.config_by_category"
    title="Configs by Category"
    requires_cursor=True
    columns=[Column("Category"),Column("Qty")]
    
    def get_queryset(self):
        return self.execute("""
            SELECT c.name,COUNT(*)
            FROM cm_config cfg
                JOIN cm_config_categories cc ON (cfg.id=cc.config_id)
                JOIN cm_objectcategory c ON (cc.objectcategory_id=c.id)
            GROUP BY 1 ORDER BY 2 DESC""")