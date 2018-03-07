# -*- coding: utf-8 -*-

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

    def backwards(self):
        db.delete_column("peer_peer", "type")
