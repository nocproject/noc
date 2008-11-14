
from south.db import db
from noc.cm.models import *

class Migration:
    
    def forwards(self):
        db.add_column("cm_config","trap_source_ip",models.IPAddressField("Trap Source IP",blank=True,null=True))
        db.add_column("cm_config","trap_community",models.CharField("Trap Community",blank=True,null=True,max_length=64))
    
    def backwards(self):
        db.delete_column("cm_config","trap_source_ip")
        db.delete_column("cm_config","trap_community")
