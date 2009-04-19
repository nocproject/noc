
from south.db import db
from noc.main.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'DatabaseStorage'
        db.create_table('main_databasestorage', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=256,unique=True)),
            ('data', BinaryField("Data")),
            ('size', models.IntegerField("Size")),
            ('mtime', models.DateTimeField("MTime"))
        ))
        
        db.send_create_signal('main', ['DatabaseStorage'])
    
    def backwards(self):
        db.delete_table('main_databasestorage')
        
