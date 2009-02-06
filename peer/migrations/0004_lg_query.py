# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'LGQueryType'
        db.create_table('peer_lgquerytype', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True))
        ))
        
        # Mock Models
        PeeringPointType = db.mock_model(model_name='PeeringPointType', db_table='peer_peeringpointtype', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        LGQueryType = db.mock_model(model_name='LGQueryType', db_table='peer_lgquerytype', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'LGQueryCommand'
        db.create_table('peer_lgquerycommand', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('peering_point_type', models.ForeignKey(PeeringPointType,verbose_name="Peering Point Type")),
            ('query_type', models.ForeignKey(LGQueryType,verbose_name="LG Query Type")),
            ('command', models.CharField("Command",max_length=128))
        ))
        db.create_index('peer_lgquerycommand', ['peering_point_type_id','query_type_id'], unique=True, db_tablespace='')
        db.send_create_signal('peer', ['LGQueryType','LGQueryCommand'])
    
    def backwards(self):
        db.delete_table('peer_lgquerycommand')
        db.delete_table('peer_lgquerytype')
        
