
from south.db import db
from django.db import models


class Migration:
    
    def forwards(self):
        db.add_column("fm_eventclass","trigger",models.CharField("Trigger",max_length=64,null=True,blank=True))
    
    def backwards(self):
        db.delete_column("fm_eventclass","trigger")
