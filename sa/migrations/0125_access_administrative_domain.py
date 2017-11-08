# Third-party modules
from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        AdministrativeDomain = db.mock_model(
            model_name="AdministrativeDomain",
            db_table="sa_administrativedomain", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)
        for t in ("sa_useraccess", "sa_groupaccess"):
            db.add_column(
                t,
                "administrative_domain",
                models.ForeignKey(AdministrativeDomain, null=True, blank=True)
            )
            db.execute("ALTER TABLE %s ALTER selector_id DROP NOT NULL" % t)

    def backwards(self):
        pass
