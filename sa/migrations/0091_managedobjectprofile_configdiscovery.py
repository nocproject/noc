# ----------------------------------------------------------------------
# managedobjectprofile config_discovery
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute(
            "ALTER TABLE sa_managedobjectprofile RENAME enable_config_polling TO enable_config_discovery"
        )
        self.db.execute(
            "ALTER TABLE sa_managedobjectprofile RENAME config_polling_min_interval TO config_discovery_min_interval"
        )
        self.db.execute(
            "ALTER TABLE sa_managedobjectprofile RENAME config_polling_max_interval TO config_discovery_max_interval"
        )
