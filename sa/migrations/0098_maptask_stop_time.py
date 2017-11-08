from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.execute("DELETE FROM sa_maptask")
        db.execute("DELETE FROM sa_reducetask")
        db.add_column("sa_maptask",
                      "stop_time",
                      models.DateTimeField()
                      )

    def backwards(self):
        db.delete_column("sa_maptask", "stop_time")
