# -*- coding: utf-8 -*-

# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column("peer_maintainer", "password",
                      models.CharField("Password", max_length=64, null=True, blank=True))
        db.delete_column("peer_maintainer", "auth")

    def backwards(self):
        db.delete_column("peer_maintainer", "password")
        db.add_column("peer_maintainer", "auth", models.TextField("auth", blank=True, null=True))
