# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# drop update_event_classification
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
        db.execute(
            "DROP FUNCTION update_event_classification(INTEGER,INTEGER,INTEGER,INTEGER,INTEGER,TEXT,TEXT,TEXT[][])"
        )

    def backwards(self):
        pass
