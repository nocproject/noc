
from south.db import db
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.delete_column("fm_eventclassificationrule","drop_event")
        
    def backwards(self):
        db.add_column("fm_eventclassificationrule","drop_event",models.BooleanField("Drop Event",default=False))
        db.execute("UPDATE fm_eventclassificationrule SET drop_event=TRUE WHERE action='D'")
