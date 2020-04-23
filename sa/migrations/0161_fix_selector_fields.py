# ----------------------------------------------------------------------
# Fix filter_name/filter_profile field types
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
          ALTER TABLE sa_managedobjectselector
          ALTER filter_profile TYPE CHAR(24)
            USING SUBSTRING("filter_profile", 1, 24)
        """
        )
        self.db.execute(
            """
          ALTER TABLE sa_managedobjectselector
          ALTER filter_name TYPE VARCHAR(256)
            USING TRIM(TRAILING ' ' FROM "filter_name")
        """
        )
