from south.db import db
from django.db import models
from noc.core.model.fields import PickledField


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
