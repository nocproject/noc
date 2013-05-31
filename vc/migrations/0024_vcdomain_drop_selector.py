# -*- coding: utf-8 -*-

## Third-party modules
from south.db import db


class Migration:
    depends_on = [
        ("sa", "0072_managedobject_set_vcdomain")
    ]

    def forwards(self):
        db.drop_column("vc_vcdomain", "selector_id")

    def backwards(self):
        pass
