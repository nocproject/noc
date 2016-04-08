from south.db import db
from django.db import models
from noc.core.model.fields import PickledField


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "metrics",
            PickledField(null=True, blank=True)
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "metrics")
