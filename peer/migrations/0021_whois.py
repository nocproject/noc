# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        # Adding model 'WhoisDatabase'
        db.create_table('peer_whoisdatabase', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField("Name", max_length=32, unique=True)),
        ))
        db.send_create_signal('peer', ['WhoisDatabase'])
        WhoisDatabase = db.mock_model(model_name='WhoisDatabase', db_table='peer_whoisdatabase', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        
        # Adding model 'WhoisLookup'
        db.create_table('peer_whoislookup', (
            ('id', models.AutoField(primary_key=True)),
            ('whois_database', models.ForeignKey(WhoisDatabase,verbose_name='Whois Database')),
            ('url', models.CharField("Object", max_length=256)),
            ('direction', models.CharField("Direction", max_length=1)),
            ('key', models.CharField("Key", max_length=32)),
            ('value', models.CharField("Value", max_length=32)),
        ))
        db.send_create_signal('peer', ['WhoisLookup'])
        WhoisLookup = db.mock_model(model_name='WhoisLookup', db_table='peer_whoislookup', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
                
        # Adding model 'WhoisCache'
        db.create_table('peer_whoiscache', (
            ('id', models.AutoField(primary_key=True)),
            ('lookup', models.ForeignKey(WhoisLookup, verbose_name="Whois Lookup")),
            ('key', models.CharField("Key", max_length=64)),        
            ('value', models.TextField("Value")),
        ))
        db.send_create_signal('peer', ['WhoisCache'])
        
        # Creating unique_together for [lookup, key] on WhoisCache.
        db.create_unique('peer_whoiscache', ['lookup_id', 'key'])
        
        # Creating unique_together for [object, key, value] on WhoisLookup.
        db.create_unique('peer_whoislookup', ['whois_database_id', 'url', 'key', 'value'])
        
    
    
    def backwards(self):
        
        # Deleting model 'WhoisLookup'
        db.delete_table('peer_whoislookup')
        
        # Deleting model 'WhoisDatabase'
        db.delete_table('peer_whoisdatabase')
                
        # Deleting model 'WhoisCache'
        db.delete_table('peer_whoiscache')
