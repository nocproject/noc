from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_huawei_ndp",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_mikrotik_ndp",
            models.BooleanField(default=False)
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "enable_box_discovery_huawei_ndp")
        db.delete_column("sa_managedobjectprofile", "enable_box_discovery_mikrotik_ndp")
