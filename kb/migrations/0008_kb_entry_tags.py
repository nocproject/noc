# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Change KBEntryTags field type
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration(object):

    def forwards(self):
        db.execute("ALTER TABLE kb_kbentry ALTER COLUMN tags TYPE text[] USING regexp_split_to_array(tags, ',')")

    def backwards(self):
        pass
