# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Drop django-tagging tables
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        for t in ["tagging_taggeditem", "tagging_tag"]:
            if db.execute("SELECT COUNT(*) FROM pg_class WHERE relname='%s'" % t)[0][0] == 1:
                db.drop_table(t)

    def backwards(self):
        pass
