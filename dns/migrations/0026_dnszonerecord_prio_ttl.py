# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dnszonerecord priority ttl
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
        db.add_column("dns_dnszonerecord", "priority", models.IntegerField("Priority", null=True, blank=True))
        db.add_column("dns_dnszonerecord", "ttl", models.IntegerField("TTL", null=True, blank=True))

    def backwards(self):
        db.delete_column("dns_dnszonerecord", "priority")
        db.delete_column("dns_dnszonerecord", "ttl")
