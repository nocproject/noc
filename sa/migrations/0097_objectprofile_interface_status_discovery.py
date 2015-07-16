from south.db import db
from django.db import models

class Migration:
    def forwards(self):
        db.add_column("sa_managedobjectprofile",
            "enable_interface_status_discovery",
            models.BooleanField("Enable caps discovery", default=True))
        db.add_column("sa_managedobjectprofile",
            "interface_status_discovery_min_interval",
            models.IntegerField("Min. caps discovery interval", default=60))
        db.add_column("sa_managedobjectprofile",
            "interface_status_discovery_max_interval",
            models.IntegerField("Max. caps discovery interval", default=300))

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "enable_interface_status_discovery")
        db.delete_column("sa_managedobjectprofile", "interface_status_discovery_min_interval")
        db.delete_column("sa_managedobjectprofile", "interface_status_discovery_max_interval")
