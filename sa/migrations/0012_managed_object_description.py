
from south.db import db
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        db.rename_column("sa_managedobject","location","description")
        
    def backwards(self):
        db.rename_column("sa_managedobject","description","location")
