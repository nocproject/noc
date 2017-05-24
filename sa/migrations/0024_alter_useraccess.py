# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration:

    def forwards(self):
        db.execute("ALTER TABLE sa_useraccess ALTER selector_id SET NOT NULL")


    def backwards(self):
        """Write your backwards migration here"""
