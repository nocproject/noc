# ----------------------------------------------------------------------
# Rename fields
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute(
            """
          ALTER TABLE sa_managedobjectprofile
          RENAME enable_box_discovery_address
          TO enable_box_discovery_address_neighbor"""
        )
        self.db.execute(
            """
          ALTER TABLE sa_managedobjectprofile
          RENAME enable_box_discovery_prefix
          TO enable_box_discovery_prefix_neighbor"""
        )
