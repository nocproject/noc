# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cleanup SubInterface's is_* indexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from noc.lib.nosql import get_db

class Migration:
    def forwards(self):
        c = get_db().noc.subinterfaces
        for i in ("is_ipv4_1", "is_ipv6_1", "is_bridge_1"):
            try:
                c.drop_index(i)
            except:
                pass

    def backwards(self):
        pass
