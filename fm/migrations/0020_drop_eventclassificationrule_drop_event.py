
from south.db import db
<<<<<<< HEAD
from django.db import models


class Migration:

    def forwards(self):
        db.delete_column("fm_eventclassificationrule", "drop_event")

    def backwards(self):
        db.add_column("fm_eventclassificationrule","drop_event", models.BooleanField("Drop Event", default=False))
=======
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.delete_column("fm_eventclassificationrule","drop_event")
        
    def backwards(self):
        db.add_column("fm_eventclassificationrule","drop_event",models.BooleanField("Drop Event",default=False))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        db.execute("UPDATE fm_eventclassificationrule SET drop_event=TRUE WHERE action='D'")
