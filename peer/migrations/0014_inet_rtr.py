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
        AS=db.mock_model(model_name='AS', db_table='peer_as', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        if db.execute("SELECT COUNT(*) FROM peer_peeringpoint")[0][0]>0:
            db.add_column("peer_peeringpoint","local_as",models.ForeignKey(AS,verbose_name="Local AS",blank=True,null=True))
            as_id=db.execute("SELECT MIN(id) FROM peer_as")[0][0]
            db.execute("UPDATE peer_peeringpoint SET local_as_id=%s",[as_id])
            db.execute("ALTER TABLE peer_peeringpoint ALTER local_as_id SET NOT NULL")
        else:
            db.add_column("peer_peeringpoint","local_as",models.ForeignKey(AS,verbose_name="Local AS"))
        db.add_column("peer_peer","masklen",models.PositiveIntegerField("Masklen",default=30))
    
    def backwards(self):
        db.delete_column("peer_peeringpoint","local_as_id")
        db.delete_column("peer_peer","masklen")
        
