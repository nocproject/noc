# -*- coding: utf-8 -*-

<<<<<<< HEAD
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):

    def forwards(self):
        # Adding field 'PeerGroup.local_pref'
        db.add_column('peer_peergroup', 'local_pref',
                      models.IntegerField("Local Pref", null=True, blank=True))
        # Adding field 'Peer.import_med'
        db.add_column('peer_peer', 'import_med',
                      models.IntegerField("Local Pref", null=True, blank=True))
        # Adding field 'PeerGroup.import_med'
        db.add_column('peer_peergroup', 'import_med',
                      models.IntegerField("Local Pref", null=True, blank=True))
        # Adding field 'Peer.export_med'
        db.add_column('peer_peer', 'export_med',
                      models.IntegerField("Local Pref", null=True, blank=True))
        # Adding field 'PeerGroup.export_med'
        db.add_column('peer_peergroup', 'export_med',
                      models.IntegerField("Local Pref", null=True, blank=True))

=======
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
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
