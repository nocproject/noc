
from south.db import db
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.execute("DROP FUNCTION update_event_classification(INTEGER,INTEGER,INTEGER,INTEGER,INTEGER,TEXT,TEXT,TEXT[][])")
    
    def backwards(self):
        "Write your backwards migration here"
