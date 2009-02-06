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
        
        # Model 'RIR'
        db.create_table('peer_rir', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("name",max_length=64,unique=True)),
            ('whois', models.CharField("whois",max_length=64,blank=True,null=True))
        ))
        
        # Mock Models
        RIR = db.mock_model(model_name='RIR', db_table='peer_rir', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'Person'
        db.create_table('peer_person', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('nic_hdl', models.CharField("nic-hdl",max_length=64,unique=True)),
            ('person', models.CharField("person",max_length=128)),
            ('address', models.TextField("address")),
            ('phone', models.TextField("phone")),
            ('fax_no', models.TextField("fax-no",blank=True,null=True)),
            ('email', models.TextField("email")),
            ('rir', models.ForeignKey(RIR,verbose_name=RIR)),
            ('extra', models.TextField("extra",blank=True,null=True))
        ))
        
        # Mock Models
        RIR = db.mock_model(model_name='RIR', db_table='peer_rir', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'Maintainer'
        db.create_table('peer_maintainer', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('maintainer', models.CharField("mntner",max_length=64,unique=True)),
            ('description', models.CharField("description",max_length=64)),
            ('auth', models.TextField("auth")),
            ('rir', models.ForeignKey(RIR,verbose_name=RIR)),
            ('extra', models.TextField("extra",blank=True,null=True))
        ))
        # Mock Models
        Maintainer = db.mock_model(model_name='Maintainer', db_table='peer_maintainer', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        Person = db.mock_model(model_name='Person', db_table='peer_person', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'Maintainer.admins'
        db.create_table('peer_maintainer_admins', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('maintainer', models.ForeignKey(Maintainer, null=False)),
            ('person', models.ForeignKey(Person, null=False))
        )) 
        
        db.send_create_signal('peer', ['RIR','Person','Maintainer'])
        for rir,whois in [
                ("ARIN","whois.arin.net"),
                ("RIPE NCC","whois.ripe.net"),
                ("APNIC","whois.apnic.net"),
                ("LACNIC","whois.lacnic.net"),
                ("AfriNIC","whois.afrinic.net")]:
            db.execute("INSERT INTO peer_rir(name,whois) VALUES(%s,%s)",[rir,whois])
    
    def backwards(self):
        db.delete_table('peer_maintainer_admins')
        db.delete_table('peer_maintainer')
        db.delete_table('peer_person')
        db.delete_table('peer_rir')
