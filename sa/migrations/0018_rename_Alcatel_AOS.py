# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# rename Alcatel AOS
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
        db.execute("UPDATE sa_managedobject SET profile_name='Alcatel.OS62xx' WHERE profile_name='Alcatel.AOS'")

    def backwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='Alcatel.AOS' WHERE profile_name='Alcatel.OS62xx'")
