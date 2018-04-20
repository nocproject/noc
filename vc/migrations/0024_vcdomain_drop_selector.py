# -*- coding: utf-8 -*-

<<<<<<< HEAD
# Third-party modules
=======
## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from south.db import db


class Migration:
    depends_on = [
        ("sa", "0072_managedobject_set_vcdomain")
    ]

    def forwards(self):
        db.drop_column("vc_vcdomain", "selector_id")

    def backwards(self):
        pass
