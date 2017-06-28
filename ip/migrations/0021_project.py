# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VRF, Prefix, Address .project field
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("ip_vrf", "project",
                      models.CharField("Project ID", max_length=256,
                                       null=True, blank=True, db_index=True))
        db.add_column("ip_prefix", "project",
                      models.CharField("Project ID", max_length=256,
                                       null=True, blank=True, db_index=True))
        db.add_column("ip_address", "project",
                      models.CharField("Project ID", max_length=256,
                                       null=True, blank=True, db_index=True))

    def backwards(self):
        db.drop_column("ip_vrf", "project")
        db.drop_column("ip_prefix", "project")
        db.drop_column("ip_address", "project")
