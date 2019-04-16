# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# change eventarchivationrule
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
        db.create_unique('fm_eventarchivationrule', ['event_class_id', 'action'])
        try:
            db.delete_unique('fm_eventarchivationrule', ['event_class_id'])
        except Exception:
            pass

    def backwards(self):
        db.delete_unique('fm_eventarchivationrule', ['event_class_id', 'action'])
        db.create_unique('fm_eventarchivationrule', ['event_class_id'])
