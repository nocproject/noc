from south.db import db
from django.db import models

class Migration:
    def forwards(self):
        db.add_column("sa_managedobjectprofile",
            "ping_interval",
            models.IntegerField("Ping interval", default=60))

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "ping_interval")
