from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("fm_eventclassificationre", "is_expression", models.BooleanField("Is Expression", default=False))

    def backwards(self):
        db.delete_column("fm_eventclassificationre", "is_expression")
