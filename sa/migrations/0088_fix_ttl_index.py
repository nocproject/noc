# ----------------------------------------------------------------------
# fix ttl index
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        c = self.mongo_db["noc.log.sa.interaction"]
        c.drop_index("expire_1")
