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
        db.add_column("peer_peeringpoint","profile_name",models.CharField("Profile",max_length=128,null=True))
        db.add_column("peer_lgquerycommand","profile_name",models.CharField("Profile",max_length=128,null=True))
        
        for id,n in db.execute("SELECT id,name FROM peer_peeringpointtype"):
            db.execute("UPDATE peer_peeringpoint SET profile_name=%s WHERE type_id=%s",[n,id])
            db.execute("UPDATE peer_lgquerycommand SET profile_name=%s WHERE peering_point_type_id=%s",[n,id])
        db.delete_column("peer_peeringpoint","type_id")
        db.delete_column("peer_lgquerycommand","peering_point_type_id")
        db.delete_table('peer_peeringpointtype')
        db.execute("ALTER TABLE peer_peeringpoint ALTER profile_name SET NOT NULL")
        db.execute("ALTER TABLE peer_lgquerycommand ALTER profile_name SET NOT NULL")
        
    
    def backwards(self):
        db.create_table('peer_peeringpointtype', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True))
        ))
        PeeringPointType = db.mock_model(model_name='PeeringPointType', db_table='peer_peeringpointtype', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        db.add_column("peer_peeringpoint","type",models.ForeignKey(PeeringPointType,null=True))
        db.add_column("peer_lgquerycommand","peering_point_type",models.ForeignKey(PeeringPointType,null=True))
        
        
        for pn, in db.execute("SELECT DISTINCT(profile_name) FROM peer_peeringpoint"):
            db.execute("INSERT INTO peer_peeringpointtype(name) VALUES(%s)",[pn])
            ppt_id=db.execute("SELECT id FROM peer_peeringpointtype WHERE name=%s",[pn])[0][0]
            db.execute("UPDATE peer_peeringpoint SET type_id=%s WHERE profile_name=%s",[ppt_id,pn])
            db.execute("UPDATE peer_lgquerycommand SET peering_point_type_id=%s WHERE profile_name=%s",[ppt_id,pn])
            
        db.delete_column("peer_peeringpoint","profile_name")
        db.delete_column("peer_lgquerycommand","profile_name")
        
        db.execute("ALTER TABLE peer_peeringpoint ALTER type_id SET NOT NULL")
        db.execute("ALTER TABLE peer_lgquerycommand ALTER peering_point_type_id SET NOT NULL")
        
        
        
