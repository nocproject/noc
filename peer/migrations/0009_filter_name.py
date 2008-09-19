
from south.db import db
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        db.add_column("peer_peer","import_filter_name",models.CharField("Import Filter Name",max_length=64,blank=True,null=True))
        db.add_column("peer_peer","export_filter_name",models.CharField("Export Filter Name",max_length=64,blank=True,null=True))
    
    def backwards(self):
        db.delete_column("peer_peer","import_filter_name")
        db.delete_column("peer_peer","export_filter_name")
