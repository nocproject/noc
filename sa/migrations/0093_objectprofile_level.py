from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("sa_managedobjectprofile",
                      "level",
                      models.IntegerField(_("Level"), default=25)
                      )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "level")
