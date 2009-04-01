
from south.db import db
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='DLink.DES3xxx' WHERE profile_name='DLink.DES35xx'")
    
    def backwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='DLink.DES35xx' WHERE profile_name='DLink.DES3xxx'")
