# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# rename Siemens
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
        db.execute("UPDATE sa_managedobject SET profile_name='NSN.hiX56xx' WHERE profile_name='Siemens.HIX5630'")

    def backwards(self):
        pass
