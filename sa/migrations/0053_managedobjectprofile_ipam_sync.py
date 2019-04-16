# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile ipam sync
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column("sa_managedobjectprofile", "sync_ipam", models.BooleanField("Sync. IPAM", default=False))
        db.add_column(
            "sa_managedobjectprofile", "fqdn_template", models.TextField("FQDN template", null=True, blank=True)
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "sync_ipam")
        db.delete_column("sa_managedobjectprofile", "fqdn_template")
