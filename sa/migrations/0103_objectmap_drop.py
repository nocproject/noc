# ----------------------------------------------------------------------
# object_map drop
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC models
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.mongo_db.noc.cache.object_map.drop()
