# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# merge EdgeCore
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
        db.execute("UPDATE sa_managedobject SET profile_name='EdgeCore.ES' WHERE profile_name LIKE 'EdgeCore.ES%%'")

    def backwards(self):
        pass
