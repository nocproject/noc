
from south.db import db
from noc.cm.models import *

class Migration:
    depends_on=(
        ("setup","0001_initial"),
        ("sa", "0001_initial"),
    )
    def forwards(self):
        
        # Model 'Object'
        db.create_table('cm_object', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('url', models.CharField("URL",max_length=128,unique=True)),
            ('profile_name', models.CharField("Profile",max_length=128))
        ))
        
        db.send_create_signal('cm', ['Object'])
    
    def backwards(self):
        db.delete_table('cm_object')
        
