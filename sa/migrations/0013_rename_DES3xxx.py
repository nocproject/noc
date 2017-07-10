# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration:

    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='DLink.DES3xxx' WHERE profile_name='DLink.DES35xx'")

    def backwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='DLink.DES35xx' WHERE profile_name='DLink.DES3xxx'")
