# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        # Adding field 'PeerGroup.local_pref'
        db.add_column('peer_peergroup', 'local_pref', models.IntegerField("Local Pref",null=True,blank=True))
        # Adding field 'Peer.import_med'
        db.add_column('peer_peer', 'import_med', models.IntegerField("Local Pref",null=True,blank=True))
        # Adding field 'PeerGroup.import_med'
        db.add_column('peer_peergroup', 'import_med', models.IntegerField("Local Pref",null=True,blank=True))
        # Adding field 'Peer.export_med'
        db.add_column('peer_peer', 'export_med', models.IntegerField("Local Pref",null=True,blank=True))
        # Adding field 'PeerGroup.export_med'
        db.add_column('peer_peergroup', 'export_med', models.IntegerField("Local Pref",null=True,blank=True))
    
    def backwards(self):
        # Deleting field 'PeerGroup.local_pref'
        db.delete_column('peer_peergroup', 'local_pref')
        # Deleting field 'Peer.import_med'
        db.delete_column('peer_peer', 'import_med')
        # Deleting field 'PeerGroup.import_med'
        db.delete_column('peer_peergroup', 'import_med')
        # Deleting field 'Peer.export_med'
        db.delete_column('peer_peer', 'export_med')
        # Deleting field 'PeerGroup.export_med'
        db.delete_column('peer_peergroup', 'export_med')
