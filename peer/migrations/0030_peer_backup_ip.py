# -*- coding: utf-8 -*-

from south.db import db
<<<<<<< HEAD
from noc.core.model.fields import INETField


class Migration:
    def forwards(self):
        # Adding field 'Peer.remote_backup_ip'
        db.add_column('peer_peer', 'remote_backup_ip',
                      INETField("Remote Backup IP", null=True,
                                blank=True))
        # Adding field 'Peer.local_backup_ip'
        db.add_column('peer_peer', 'local_backup_ip',
                      INETField("Local Backup IP", null=True,
                                blank=True))

=======
from django.db import models
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        # Adding field 'Peer.remote_backup_ip'
        db.add_column('peer_peer', 'remote_backup_ip', INETField("Remote Backup IP",null=True,blank=True))
        # Adding field 'Peer.local_backup_ip'
        db.add_column('peer_peer', 'local_backup_ip', INETField("Local Backup IP",null=True,blank=True))
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        # Deleting field 'Peer.remote_backup_ip'
        db.delete_column('peer_peer', 'remote_backup_ip')
        # Deleting field 'Peer.local_backup_ip'
        db.delete_column('peer_peer', 'local_backup_ip')
