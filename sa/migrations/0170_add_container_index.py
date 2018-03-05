# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.create_index(
            "sa_managedobject",
            ["container"], unique=False, db_tablespace="")
