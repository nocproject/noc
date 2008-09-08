
from south.db import db
from noc.setup.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'Settings'
        db.create_table('setup_settings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('key', models.CharField("Key",max_length=64,unique=True)),
            ('value', models.CharField("Value",max_length=256)),
            ('default', models.CharField("Default",max_length=256))
        ))
        
        db.send_create_signal('setup', ['Settings'])
    
    def backwards(self):
        db.delete_table('setup_settings')
        
