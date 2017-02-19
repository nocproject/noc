from south.db import db
from django.db import models


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_lacp",
            models.BooleanField(default=False)
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "enable_box_discovery_lacp")
