# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.peer.models import *
from noc.lib.fields import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'PrefixListCache'
        db.create_table('peer_prefixlistcache', (
            ('id', models.AutoField(primary_key=True)),
            ('peering_point', models.ForeignKey(orm.PeeringPoint, verbose_name="Peering Point")),
            ('name', models.CharField("Name", max_length=64)),
            ('data', InetArrayField("Data")),
            ('strict', models.BooleanField("Strict")),
            ('changed', models.DateTimeField("Changed", auto_now=True, auto_now_add=True)),
            ('pushed', models.DateTimeField("Pushed", null=True, blank=True)),
        ))
        db.send_create_signal('peer', ['PrefixListCache'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'PrefixListCache'
        db.delete_table('peer_prefixlistcache')
        
    
    
    models = {
        'peer.peeringpoint': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    
