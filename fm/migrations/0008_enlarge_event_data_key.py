
from south.db import db
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.execute("ALTER TABLE fm_eventdata ALTER key TYPE VARCHAR(256)")
    
    def backwards(self):
        db.execute("ALTER TABLE fm_eventdata ALTER key TYPE VARCHAR(64)")
