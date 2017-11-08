from noc.core.model.fields import PickledField
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "metrics",
            PickledField(null=True, blank=True)
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "metrics")
