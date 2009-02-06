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
        
        # Model 'LIR'
        db.create_table('peer_lir', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("LIR name",unique=True,max_length=64))
        ))
        
        # Mock Models
        LIR = db.mock_model(model_name='LIR', db_table='peer_lir', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'AS'
        db.create_table('peer_as', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('lir', models.ForeignKey(LIR,verbose_name=LIR)),
            ('asn', models.IntegerField("ASN",unique=True)),
            ('description', models.CharField("Description",max_length=64)),
            ('rpsl_header', models.TextField("RPSL Header",null=True,blank=True)),
            ('rpsl_footer', models.TextField("RPSL Footer",null=True,blank=True))
        ))
        # Model 'ASSet'
        db.create_table('peer_asset', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('description', models.CharField("Description",max_length=64)),
            ('members', models.TextField("Members",null=True,blank=True)),
            ('rpsl_header', models.TextField("RPSL Header",null=True,blank=True)),
            ('rpsl_footer', models.TextField("RPSL Footer",null=True,blank=True))
        ))
        # Model 'PeeringPointType'
        db.create_table('peer_peeringpointtype', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True))
        ))
        
        # Mock Models
        PeeringPointType = db.mock_model(model_name='PeeringPointType', db_table='peer_peeringpointtype', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'PeeringPoint'
        db.create_table('peer_peeringpoint', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hostname', models.CharField("FQDN",max_length=64,unique=True)),
            ('router_id', models.IPAddressField("Router-ID",unique=True)),
            ('type', models.ForeignKey(PeeringPointType,verbose_name="Type")),
            ('communities', models.CharField("Import Communities",max_length=128,blank=True,null=True))
        ))
        # Model 'PeerGroup'
        db.create_table('peer_peergroup', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('description', models.CharField("Description",max_length=64)),
            ('communities', models.CharField("Import Communities",max_length=128,blank=True,null=True)),
            ('max_prefixes', models.IntegerField("Max. Prefixes",default=100))
        ))
        
        # Mock Models
        PeerGroup = db.mock_model(model_name='PeerGroup', db_table='peer_peergroup', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        PeeringPoint = db.mock_model(model_name='PeeringPoint', db_table='peer_peeringpoint', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        AS = db.mock_model(model_name='AS', db_table='peer_as', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'Peer'
        db.create_table('peer_peer', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('peer_group', models.ForeignKey(PeerGroup,verbose_name="Peer Group")),
            ('peering_point', models.ForeignKey(PeeringPoint,verbose_name="Peering Point")),
            ('local_asn', models.ForeignKey(AS,verbose_name="Local AS")),
            ('local_ip', models.IPAddressField("Local IP")),
            ('remote_asn', models.IntegerField("Remote AS")),
            ('remote_ip', models.IPAddressField("Remote IP")),
            ('import_filter', models.CharField("Import filter",max_length=64)),
            ('local_pref', models.IntegerField("Local Pref",null=True,blank=True)),
            ('export_filter', models.CharField("Export filter",max_length=64)),
            ('description', models.CharField("Description",max_length=64,null=True,blank=True)),
            ('tt', models.IntegerField("TT",blank=True,null=True)),
            ('communities', models.CharField("Import Communities",max_length=128,blank=True,null=True)),
            ('max_prefixes', models.IntegerField("Max. Prefixes",default=100))
        ))
        
        db.send_create_signal('peer', ['LIR','AS','ASSet','PeeringPointType','PeeringPoint','PeerGroup','Peer'])
    
    def backwards(self):
        db.delete_table('peer_peer')
        db.delete_table('peer_peergroup')
        db.delete_table('peer_peeringpoint')
        db.delete_table('peer_peeringpointtype')
        db.delete_table('peer_asset')
        db.delete_table('peer_as')
        db.delete_table('peer_lir')
        
