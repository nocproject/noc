# -*- coding: utf-8 -*-

from south.db import db


class Migration:
    def forwards(self):
        db.create_index("fm_event", ["status"])
        db.create_index("fm_event", ["timestamp"])

    def backwards(self):
        db.delete_index("fm_event", ["status"])
        db.delete_index("fm_event", ["timestamp"])
