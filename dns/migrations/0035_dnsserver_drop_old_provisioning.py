# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dnsserver drop old provisioning
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
        for c in ["generator_name", "location", "provisioning", "autozones_path"]:
            db.delete_column("dns_dnsserver", c)

    def backwards(self):
        pass
