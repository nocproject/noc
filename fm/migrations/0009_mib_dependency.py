
from south.db import db
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        MIB = db.mock_model(model_name='MIB', db_table='fm_mib', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        MIB = db.mock_model(model_name='MIB', db_table='fm_mib', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'MIBDependency'
        db.create_table('fm_mibdependency', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mib', models.ForeignKey(MIB,verbose_name=MIB)),
            ('requires_mib', models.ForeignKey(MIB,verbose_name="Requires MIB",related_name="requiredbymib_set"))
        ))
        db.create_index('fm_mibdependency', ['mib_id','requires_mib_id'], unique=True, db_tablespace='')
        
        
        db.send_create_signal('fm', ['MIBDependency'])
    
    def backwards(self):
        db.delete_table('fm_mibdependency')
        
