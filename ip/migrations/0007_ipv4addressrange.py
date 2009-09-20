# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.ip.models import *

class Migration:
    
    def forwards(self):
        VRF = db.mock_model(model_name='VRF', db_table='ip_vrf', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        # Adding model 'IPv4AddressRange'
        db.create_table('ip_ipv4addressrange', (
            ('id', models.AutoField(primary_key=True)),
            ('vrf', models.ForeignKey(VRF, verbose_name="VRF")),
            ('name', models.CharField("Name", max_length=64)),
            ('from_ip', models.IPAddressField("From IP")),
            ('to_ip', models.IPAddressField("To Address")),
            ('description', models.TextField("Description", null=True, blank=True)),
            ('is_locked', models.BooleanField("Range is locked", default=False)),        
            ('fqdn_action', models.CharField("FQDN Action", default='N', max_length=1)),
            ('fqdn_action_parameter', models.CharField("FQDN Action Parameter", max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('ip', ['IPv4AddressRange'])
        
        # Creating unique_together for [vrf, name] on IPv4AddressRange.
        db.create_unique('ip_ipv4addressrange', ['vrf_id', 'name'])
        
    
    
    def backwards(self):
        
        # Deleting model 'IPv4AddressRange'
        db.delete_table('ip_ipv4addressrange')
        
        # Deleting unique_together for [vrf, name] on IPv4AddressRange.
        db.delete_unique('ip_ipv4addressrange', ['vrf_id', 'name'])
