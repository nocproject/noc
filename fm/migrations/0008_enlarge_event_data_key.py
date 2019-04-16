# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# enlarge event data key
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
        db.execute("ALTER TABLE fm_eventdata ALTER key TYPE VARCHAR(256)")

    def backwards(self):
        db.execute("ALTER TABLE fm_eventdata ALTER key TYPE VARCHAR(64)")
