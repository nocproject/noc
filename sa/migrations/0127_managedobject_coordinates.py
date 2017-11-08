from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("sa_managedobject", "x",
                      models.FloatField(null=True, blank=True))
        db.add_column("sa_managedobject", "y",
                      models.FloatField(null=True, blank=True))
        db.add_column("sa_managedobject", "default_zoom",
                      models.IntegerField(null=True, blank=True))

    def backwards(self):
        db.delete_column("sa_managedobject", "x")
        db.delete_column("sa_managedobject", "y")
        db.delete_column("sa_managedobject", "default_zoom")
