# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# extend dnszone name
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.execute("ALTER TABLE dns_dnszone ALTER name TYPE VARCHAR(256)")

    def backwards(self):
        db.execute("ALTER TABLE dns_dnszone ALTER name TYPE VARCHAR(64)")
