# -*- coding: utf-8 -*-

<<<<<<< HEAD
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):

    def forwards(self):
        db.add_column("peer_peer", "rpsl_remark",
                      models.CharField("RPSL Remark", max_length=64, null=True, blank=True))

    def backwards(self):
        db.delete_column("peer_peer", "rpsl_remark")
=======
from south.db import db
from django.db import models
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        db.add_column("peer_peer","rpsl_remark",models.CharField("RPSL Remark",max_length=64,null=True,blank=True))
    
    def backwards(self):
        db.delete_column("peer_peer","rpsl_remark")

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
