from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("sa_managedobjectprofile",
                      "enable_id_discovery",
                      models.BooleanField("Enable ID discovery", default=True))
        db.add_column("sa_managedobjectprofile",
                      "id_discovery_min_interval",
                      models.IntegerField("Min. ID discovery interval", default=600))
        db.add_column("sa_managedobjectprofile",
                      "id_discovery_max_interval",
                      models.IntegerField("Max. ID discovery interval", default=86400))

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "enable_id_discovery")
        db.delete_column("sa_managedobjectprofile", "id_discovery_min_interval")
        db.delete_column("sa_managedobjectprofile", "id_discovery_max_interval")
