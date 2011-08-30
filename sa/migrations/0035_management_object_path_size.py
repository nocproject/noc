# encoding: utf-8
import datetime
from south.db import db

class Migration:
    def forwards(self):
        db.execute("ALTER TABLE sa_managedobject ALTER remote_path TYPE VARCHAR(256)")
    
    def backwards(self):
        db.execute("ALTER TABLE sa_managedobject ALTER remote_path TYPE VARCHAR(32)")
    
