# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.dns.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'DNSZoneProfile'
        db.create_table('dns_dnszoneprofile', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('zone_transfer_acl', models.CharField("named zone transfer ACL",max_length=64)),
            ('zone_ns_list', models.CharField("NS list",max_length=64)),
            ('zone_soa', models.CharField("SOA",max_length=64)),
            ('zone_contact', models.CharField("Contact",max_length=64)),
            ('zone_refresh', models.IntegerField("Refresh",default=3600)),
            ('zone_retry', models.IntegerField("Retry",default=900)),
            ('zone_expire', models.IntegerField("Expire",default=86400)),
            ('zone_ttl', models.IntegerField("TTL",default=3600))
        ))
        
        # Mock Models
        DNSZoneProfile = db.mock_model(model_name='DNSZoneProfile', db_table='dns_dnszoneprofile', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'DNSZone'
        db.create_table('dns_dnszone', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Domain",max_length=64,unique=True)),
            ('description', models.CharField("Description",null=True,blank=True,max_length=64)),
            ('is_auto_generated', models.BooleanField("Auto generated?")),
            ('serial', models.CharField("Serial",max_length=10,default="0000000000")),
            ('profile', models.ForeignKey(DNSZoneProfile,verbose_name="Profile"))
        ))
        # Model 'DNSZoneRecordType'
        db.create_table('dns_dnszonerecordtype', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('type', models.CharField("Type",max_length=16,unique=True)),
        ))
        
        # Mock Models
        DNSZone = db.mock_model(model_name='DNSZone', db_table='dns_dnszone', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        DNSZoneRecordType = db.mock_model(model_name='DNSZoneRecordType', db_table='dns_dnszonerecordtype', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'DNSZoneRecord'
        db.create_table('dns_dnszonerecord', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('zone', models.ForeignKey(DNSZone,verbose_name="Zone")),
            ('left', models.CharField("Left",max_length=32,blank=True,null=True)),
            ('type', models.ForeignKey(DNSZoneRecordType,verbose_name="Type")),
            ('right', models.CharField("Right",max_length=64))
        ))
        
        db.send_create_signal('dns', ['DNSZoneProfile','DNSZone','DNSZoneRecordType','DNSZoneRecord'])
    
    def backwards(self):
        db.delete_table('dns_dnszonerecord')
        db.delete_table('dns_dnszonerecordtype')
        db.delete_table('dns_dnszone')
        db.delete_table('dns_dnszoneprofile')
        
