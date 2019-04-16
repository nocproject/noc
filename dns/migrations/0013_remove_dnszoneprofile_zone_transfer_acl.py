# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# remove zone_transfer_acl
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
        db.delete_column("dns_dnszoneprofile", "zone_transfer_acl")

    def backwards(self):
        db.add_column(
            "dns_dnszoneprofile", "zone_transfer_acl",
            models.CharField("named zone transfer ACL", max_length=64, default="acl-transfer")
        )
