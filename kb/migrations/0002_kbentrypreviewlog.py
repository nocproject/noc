
from south.db import db
from noc.kb.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        KBEntry = db.mock_model(model_name='KBEntry', db_table='kb_kbentry', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'KBEntryPreviewLog'
        db.create_table('kb_kbentrypreviewlog', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('kb_entry', models.ForeignKey(KBEntry,verbose_name="KB Entry")),
            ('timestamp', models.DateTimeField("Timestamp",auto_now_add=True)),
            ('user', models.ForeignKey(User,verbose_name=User))
        ))
        
        db.send_create_signal('kb', ['KBEntryPreviewLog'])
    
    def backwards(self):
        db.delete_table('kb_kbentrypreviewlog')
        
