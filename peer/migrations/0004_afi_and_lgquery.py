
from south.db import db
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'AFI'
        db.create_table('peer_afi', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('afi', models.CharField("AFI",max_length=10,unique=True))
        ))
        
        # Mock Models
        PeeringPoint = db.mock_model(model_name='PeeringPoint', db_table='peer_peeringpoint', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        AFI = db.mock_model(model_name='AFI', db_table='peer_afi', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'LGQuery'
        db.create_table('peer_lgquery', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('peering_point_type', models.ForeignKey(PeeringPointType,verbose_name=PeeringPointType)),
            ('afi', models.ForeignKey(AFI,verbose_name=AFI)),
            ('query', models.CharField("Query",max_length=32)),
            ('command', models.CharField("Command",max_length=128))
        ))
        db.create_index('peer_lgquery', ['peering_point_type_id','afi_id','query'], unique=True, db_tablespace='')        
        db.send_create_signal('peer', ['AFI','LGQuery'])
    
    def backwards(self):
        db.delete_table('peer_lgquery')
        db.delete_table('peer_afi')
        
