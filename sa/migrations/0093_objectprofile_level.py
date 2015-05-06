from south.db import db
from django.db import models

class Migration:
    def forwards(self):
        db.add_column("sa_managedobjectprofile",
            "level",
            models.IntegerField(_("Level"), default=25)
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "level")
