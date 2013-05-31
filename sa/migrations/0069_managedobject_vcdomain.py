# encoding: utf-8
from south.db import db
from django.db import models


class Migration:
    depends_on = [
        ("vc", "0001_initial")
    ]

    def forwards(self):
        VCDomain = db.mock_model(
            model_name="VCDomain",
            db_table="vc_vcdomain",
            db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField
        )
        db.add_column("sa_managedobject", "vc_domain",
                      models.ForeignKey(VCDomain,
                                        null=True, blank=True))

    def backwards(self):
        db.delete_column("sa_managedobject", "vc_domain_id")
