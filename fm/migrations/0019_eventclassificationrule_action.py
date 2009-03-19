
from south.db import db
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.add_column("fm_eventclassificationrule","action",models.CharField("Action",max_length=1,choices=[("A","Make Active"),("C","Close"),("D","Drop")],default="A"))
        db.execute("UPDATE fm_eventclassificationrule SET action='D' WHERE drop_event=TRUE")

    def backwards(self):
        db.delete_column("fm_eventclassificationrule","action")
