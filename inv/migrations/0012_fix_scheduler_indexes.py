# ---------------------------------------------------------------------
# Drop scheduler indexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.core.migration.base import BaseMigration

logger = logging.getLogger(__name__)


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        for c in db.list_collection_names():
            if c.startswith("noc.schedules."):
                db[c].drop_indexes()
