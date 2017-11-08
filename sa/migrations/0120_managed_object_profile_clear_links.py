from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "clear_links_on_platform_change",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "clear_links_on_serial_change",
            models.BooleanField(default=False)
        )

    def backwards(self):
        pass
