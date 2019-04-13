# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# rename DES3xxx
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
        db.execute("UPDATE sa_managedobject SET profile_name='DLink.DES3xxx' WHERE profile_name='DLink.DES35xx'")

    def backwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='DLink.DES35xx' WHERE profile_name='DLink.DES3xxx'")
