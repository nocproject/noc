# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column("peer_peeringpoint", "location",
                      models.CharField("Location", max_length=64, blank=True, null=True))

    def backwards(self):
        db.delete_column("peer_peeringpoint", "location")
