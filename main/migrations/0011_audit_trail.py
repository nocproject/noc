
from south.db import db
from noc.main.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'AuditTrail'
        db.create_table('main_audittrail', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(User,verbose_name=User)),
            ('timestamp', models.DateTimeField("Timestamp",auto_now=True)),
            ('model', models.CharField("Model",max_length=128)),
            ('db_table', models.CharField("Table",max_length=128)),
            ('operation', models.CharField("Operation",max_length=1,choices=[("C","Create"),("M","Modify"),("D","Delete")])),
            ('subject', models.CharField("Subject",max_length=256)),
            ('body', models.TextField("Body"))
        ))
        
        db.send_create_signal('main', ['AuditTrail'])
    
    def backwards(self):
        db.delete_table('main_audittrail')
        
