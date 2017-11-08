# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("dns_dnsserver", "ip",
                      models.IPAddressField("IP", null=True, blank=True))

    def backwards(self):
        db.delete_column("dns_dnsserver", "ip")
