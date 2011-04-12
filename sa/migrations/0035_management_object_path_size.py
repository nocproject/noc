# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):
    def forwards(self):
        db.execute("ALTER TABLE sa_managedobject ALTER remote_path TYPE VARCHAR(256)")
    
    def backwards(self):
        db.execute("ALTER TABLE sa_managedobject ALTER remote_path TYPE VARCHAR(32)")
    
