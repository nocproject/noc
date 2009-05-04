
from south.db import db
from noc.kb.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        KBEntry = db.mock_model(model_name='KBEntry', db_table='kb_kbentry', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'KBGlobalBookmark'
        db.create_table('kb_kbglobalbookmark', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('kb_entry', models.ForeignKey(KBEntry,verbose_name=KBEntry,unique=True))
        ))
        
        # Mock Models
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        KBEntry = db.mock_model(model_name='KBEntry', db_table='kb_kbentry', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'KBUserBookmark'
        db.create_table('kb_kbuserbookmark', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(User,verbose_name=User)),
            ('kb_entry', models.ForeignKey(KBEntry,verbose_name=KBEntry))
        ))
        db.create_index('kb_kbuserbookmark', ['user_id','kb_entry_id'], unique=True, db_tablespace='')
        
        
        db.send_create_signal('kb', ['KBGlobalBookmark','KBUserBookmark'])
    
    def backwards(self):
        db.delete_table('kb_kbuserbookmark')
        db.delete_table('kb_kbglobalbookmark')
        
