# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# add container index
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
        db.create_index("sa_managedobject", ["container"], unique=False, db_tablespace="")
