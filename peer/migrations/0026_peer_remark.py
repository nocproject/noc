# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        db.add_column("peer_peer","rpsl_remark",models.CharField("RPSL Remark",max_length=64,null=True,blank=True))
    
    def backwards(self, orm):
        db.delete_column("peer_peer","rpsl_remark")

