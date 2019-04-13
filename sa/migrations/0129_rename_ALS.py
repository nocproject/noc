# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# rename ALS
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
        db.execute("UPDATE sa_managedobject SET profile_name='Alsitec.7200' WHERE profile_name LIKE 'ALS.7200'")

    def backwards(self):
        pass
