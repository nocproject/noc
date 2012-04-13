
from south.db import db
from noc.main.models import *
from noc.lib.fields import PickledField


class Migration:
    
    def forwards(self):
        
        # Model 'Language'
        db.create_table('main_changesquarantine', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('timestamp', models.DateTimeField("Timestamp",auto_now_add=True)),
            ('changes_type', models.CharField("Type",max_length=64)),
            ('subject', models.CharField("Subject",max_length=256)),
            ('data', PickledField("Data")),
        ))
        
        db.create_table('main_changesquarantinerule', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True)),
            ('is_active', models.BooleanField("Is Active",default=True)),
            ('changes_type', models.CharField("Type",max_length=64)),
            ('subject_re', models.CharField("Subject",max_length=256)),
            ('action', models.CharField("Action",max_length=1,choices=[("I","Ignore"),("A","Accept"),("Q","Quarantine")])),
            ('description', models.TextField("Description",null=True,blank=True)),
        ))
        
        db.send_create_signal('main', ['ChangesQuarantine','ChangesQuarantineRule'])
    
    def backwards(self):
        db.delete_table('main_changesquarantine')
        db.delete_table('main_changesquarantinerule')
