# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dnszone paid_till
# ----------------------------------------------------------------------
# Copyright (C) 2009-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column("dns_dnszone", "paid_till", models.DateField("Paid Tille", null=True, blank=True))

    def backwards(self):
        db.delete_column("dns_dnszone", "paid_till")
