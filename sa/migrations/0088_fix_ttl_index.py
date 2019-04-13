# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# fix ttl index
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        c = get_db()["noc.log.sa.interaction"]
        c.drop_index("expire_1")

    def backwards(self):
        pass
