
from south.db import db
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.execute("UPDATE fm_event SET status='U' WHERE subject IS NULL")
        db.execute("UPDATE fm_event SET status='C' WHERE subject IS NOT NULL AND \"timestamp\"<('now'::timestamp-'1day'::interval)")
        db.execute("UPDATE fm_event SET status='A' WHERE subject IS NOT NULL AND \"timestamp\">=('now'::timestamp-'1day'::interval)")
            
    def backwards(self):
        "Write your backwards migration here"
