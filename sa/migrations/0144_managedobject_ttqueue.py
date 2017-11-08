from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobject",
            "tt_queue",
            models.CharField(max_length=64, null=True, blank=True)
        )

    def backwards(self):
        db.delete_column("sa_managedobject", "tt_queue")
