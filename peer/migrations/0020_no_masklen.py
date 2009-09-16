# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.peer.models import *

class Migration:
    def forwards(self):
        for peer_id,local_ip,remote_ip,masklen in db.execute("SELECT id,local_ip,remote_ip,masklen FROM peer_peer"):
            if "/" not in local_ip:
                local_ip+="/%d"%masklen
            if "/" not in remote_ip:
                remote_ip+="/%d"%masklen
            db.execute("UPDATE peer_peer SET local_ip=%s,remote_ip=%s WHERE id=%s",[local_ip,remote_ip,peer_id])
        db.execute("COMMIT")
        db.drop_column("peer_peer","masklen")
    
    def backwards(self):
        pass
