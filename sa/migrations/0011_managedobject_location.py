
from south.db import db
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        db.add_column("sa_managedobject","location",models.CharField("Location",max_length=256,null=True,blank=True))
    
    def backwards(self):
        db.delete_column("sa_managedobject","location")
