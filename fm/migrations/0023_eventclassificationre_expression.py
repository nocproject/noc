
from south.db import db
from django.db import models


class Migration:

    def forwards(self):
        db.add_column("fm_eventclassificationre","is_expression",models.BooleanField("Is Expression",default=False))

    def backwards(self):
        db.delete_column("fm_eventclassificationre","is_expression")
