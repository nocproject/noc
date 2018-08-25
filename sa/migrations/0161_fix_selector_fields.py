# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Fix filter_name/filter_profile field types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.execute("""
          ALTER TABLE sa_managedobjectselector 
          ALTER filter_profile TYPE CHAR(24) 
            USING SUBSTRING("filter_profile", 1, 24)
        """)
        db.execute("""
          ALTER TABLE sa_managedobjectselector 
          ALTER filter_name TYPE VARCHAR(256) 
            USING TRIM(TRAILING ' ' FROM "filter_name")
        """)

    def backwards(self):
        pass
