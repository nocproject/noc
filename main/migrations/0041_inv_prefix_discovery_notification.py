# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv prefix_discovery notification
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
        if db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",
                      ["inv.prefix_discovery"])[0][0] == 0:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)", ["inv.prefix_discovery"])

    def backwards(self):
        pass
