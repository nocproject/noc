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
        # Mock Models
        DNSZoneProfile = db.mock_model(model_name='DNSZoneProfile', db_table='dns_dnszoneprofile', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        DNSServer = db.mock_model(model_name='DNSServer', db_table='dns_dnsserver', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'DNSZoneProfile.masters'
        db.create_table('dns_dnszoneprofile_masters', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dnszoneprofile', models.ForeignKey(DNSZoneProfile, null=False)),
            ('dnsserver', models.ForeignKey(DNSServer, null=False))
        )) 
        # Mock Models
        DNSZoneProfile = db.mock_model(model_name='DNSZoneProfile', db_table='dns_dnszoneprofile', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        DNSServer = db.mock_model(model_name='DNSServer', db_table='dns_dnsserver', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'DNSZoneProfile.slaves'
        db.create_table('dns_dnszoneprofile_slaves', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dnszoneprofile', models.ForeignKey(DNSZoneProfile, null=False)),
            ('dnsserver', models.ForeignKey(DNSServer, null=False))
        ))
        db.execute("INSERT INTO dns_dnszoneprofile_masters(dnszoneprofile_id,dnsserver_id) SELECT dnszoneprofile_id,dnsserver_id FROM dns_dnszoneprofile_ns_servers")
        db.delete_table('dns_dnszoneprofile_ns_servers')
        
        db.send_create_signal('dns', ['DNSZoneProfile'])
    
    def backwards(self):
        # Mock Models
        DNSZoneProfile = db.mock_model(model_name='DNSZoneProfile', db_table='dns_dnszoneprofile', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        DNSServer = db.mock_model(model_name='DNSServer', db_table='dns_dnsserver', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'DNSZoneProfile.slaves'
        db.create_table('dns_dnszoneprofile_ns_servers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dnszoneprofile', models.ForeignKey(DNSZoneProfile, null=False)),
            ('dnsserver', models.ForeignKey(DNSServer, null=False))
        ))
        db.execute("INSERT INTO dns_dnszoneprofile_ns_servers(dnszoneprofile_id,dnsserver_id) SELECT dnszoneprofile_id,dnsserver_id FROM dns_dnszoneprofile_masters UNION SELECT dnszoneprofile_id,dnsserver_id FROM dns_dnszoneprofile_slaves")
        
        db.delete_table('dns_dnszoneprofile_masters')
        db.delete_table('dns_dnszoneprofile_slaves')
