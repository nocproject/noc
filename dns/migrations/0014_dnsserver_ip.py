# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dnsserver ip
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
        db.add_column("dns_dnsserver", "ip", models.IPAddressField("IP", null=True, blank=True))

    def backwards(self):
        db.delete_column("dns_dnsserver", "ip")
