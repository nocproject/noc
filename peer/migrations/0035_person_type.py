# -*- coding: utf-8 -*-

<<<<<<< HEAD
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):

    def forwards(self):
        db.add_column(
            "peer_person",
            "type", models.CharField(
                "type", max_length=1, default="P",
                choices=[
                    ("P", "Person"),
                    ("R", "Role")
                ]
            )
        )
=======
from south.db import db
from django.db import models
from noc.peer.models import *

class Migration:

    def forwards(self):
        db.add_column("peer_person",
            "type", models.CharField("type", max_length=1, default="P",
                    choices=[("P", "Person"), ("R", "Role")]))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def backwards(self):
        db.delete_column("peer_peer", "type")
