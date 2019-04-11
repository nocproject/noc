# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ip_address index address
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
        db.create_index("ip_address", ["address"], db_tablespace="")

    def backwards(self):
        pass
