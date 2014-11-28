from south.db import db
from django.db import models

class Migration:
    def forwards(self):
        db.execute("ALTER TABLE sa_managedobjectprofile RENAME enable_config_polling TO enable_config_discovery")
        db.execute("ALTER TABLE sa_managedobjectprofile RENAME config_polling_min_interval TO config_discovery_min_interval")
        db.execute("ALTER TABLE sa_managedobjectprofile RENAME config_polling_max_interval TO config_discovery_max_interval")

    def backwards(self):
        pass
