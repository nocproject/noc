# -*- coding: utf-8 -*-

<<<<<<< HEAD
# Third-party modules
from south.db import db
# NOC modules
=======
## Third-party modules
from south.db import db
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from django.db import models


class Migration:
    depends_on = [
        ("main", "0027_style")
    ]

    def forwards(self):
        Style = db.mock_model(model_name="Style", db_table="main_style",
            db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        db.add_column("vc_vcdomain", "style",
            models.ForeignKey(Style,
                verbose_name="Style",
                null=True, blank=True))
        db.add_column("vc_vc", "style",
            models.ForeignKey(Style,
                verbose_name="Style",
                null=True, blank=True))

    def backwards(self):
        db.drop_column("vc_vcdomain", "style_id")
        db.drop_column("vc_vc", "style_id")
