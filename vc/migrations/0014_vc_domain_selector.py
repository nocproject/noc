# -*- coding: utf-8 -*-

## Third-party modules
from south.db import db
## NOC modules
from noc.vc.models import *


class Migration:
    def forwards(self):
        ManagedObjectSelector = db.mock_model(
            model_name="ManagedObjectSelector",
            db_table="sa_managedobjectselector", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)
        db.add_column("vc_vcdomain", "selector",
                      models.ForeignKey(ManagedObjectSelector,
                                        verbose_name="Selector",
                                        null=True, blank=True))

    def backwards(self):
        db.drop_column("vc_vcdomain", "selector")
