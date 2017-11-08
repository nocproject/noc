# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Drop scheduler indexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.lib.nosql import get_db

logger = logging.getLogger(__name__)


class Migration(object):
    def forwards(self):
        db = get_db()
        for c in db.collection_names():
            if c.startswith("noc.schedules."):
                db[c].drop_indexes()

    def backwards(self):
        pass
