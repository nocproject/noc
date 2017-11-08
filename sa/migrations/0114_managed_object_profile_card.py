from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("sa_managedobjectprofile",
                      "card",
                      models.CharField(
                          "Card name",
                          max_length=256, blank=True, null=True,
                          default="managedobject"
                      )
                      )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "card")
