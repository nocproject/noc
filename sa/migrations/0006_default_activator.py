
from south.db import db
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM sa_activator")[0][0]==0:
            db.execute("INSERT INTO sa_activator(name,ip,is_active) VALUES('default','127.0.0.1',true)")
    
    def backwards(self):
        "Write your backwards migration here"
