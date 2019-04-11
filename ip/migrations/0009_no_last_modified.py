# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# no last modified
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
        db.delete_column("ip_ipv4block", "modified_by_id")
        db.delete_column("ip_ipv4block", "last_modified")
        db.delete_column("ip_ipv4address", "modified_by_id")
        db.delete_column("ip_ipv4address", "last_modified")

    def backwards(self):
        pass
