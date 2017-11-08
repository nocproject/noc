# -*- coding: utf-8 -*-

from django.db import models
from noc.peer.models import *
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("peer_peer", "status", models.CharField("Status", max_length=1, default="A",
                                                              choices=[("P", "Planned"), ("A", "Active"),
                                                                       ("S", "Shutdown")]))

    def backwards(self):
        db.delete_column("peer_peer", "status")
