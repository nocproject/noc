# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration(object):
    depends_on = (
        ("cm", "0016_no_objectgroup"),
    )

    def forwards(self):
        for t in ["sa_managedobject_groups", "sa_managedobjectselector_filter_groups", "sa_objectgroup"]:
            db.drop_table(t)

    def backwards(self):
        pass
