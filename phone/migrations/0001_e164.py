# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# e164
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        coll = db["noc.dialplans"]
        if not coll.count_documents({}):
            coll.insert_one(
                {"name": "E.164", "description": "E.164 numbering plan", "mask": r"\d{3,15}"}
            )
