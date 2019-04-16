# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# finish tag migration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    TAG_MODELS = ["dns_dnszone", "dns_dnszonerecord"]

    def forwards(self):
        # Drop old tags
        for m in self.TAG_MODELS:
            db.drop_column(m, "tags")
        # Rename new tags
        for m in self.TAG_MODELS:
            db.rename_column(m, "tmp_tags", "tags")
        # Create indexes
        for m in self.TAG_MODELS:
            db.execute("CREATE INDEX x_%s_tags ON \"%s\" USING GIN(\"tags\")" % (m, m))

    def backwards(self):
        pass
