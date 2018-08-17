# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Default stomp users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        s = get_db().noc.stomp_access
        if not s.count_documents({}):
            s.insert({"user": "noc", "password": "noc", "is_active": True})

    def backwards(self):
        pass
