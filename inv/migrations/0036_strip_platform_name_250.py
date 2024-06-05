# ----------------------------------------------------------------------
# Strict Platform name to 200
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration

MAX_PLATFORM_LENGTH = 200


class Migration(BaseMigration):
    def migrate(self):
        platform_coll = self.mongo_db["noc.platforms"]
        bulk = []
        duplicates = defaultdict(int)
        for p in platform_coll.find({}, {"name": 1}):
            m_name = p["name"][:MAX_PLATFORM_LENGTH]
            if p["name"] != m_name:
                duplicates[m_name] += 1
                if m_name in duplicates:
                    m_name += f"_{duplicates[m_name]}"
                bulk += [UpdateOne({"_id": p["_id"]}, {"$set": {"name": m_name}})]
        if bulk:
            platform_coll.bulk_write(bulk)
