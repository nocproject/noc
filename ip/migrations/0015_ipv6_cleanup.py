# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ipv6 cleanup
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
        # VRFGroup
        db.delete_column("ip_vrfgroup", "unique_addresses")
        # Delete obsolete tables
        db.delete_table("ip_ipv4block")
        db.delete_table("ip_ipv4address")
        db.delete_table("ip_ipv4blockaccess")
        db.delete_table("ip_ipv4blockbookmark")
        db.delete_table("ip_ipv4addressrange")
        db.execute("DROP FUNCTION free_ip(INTEGER,CIDR)")

    def backwards(self):
        pass
