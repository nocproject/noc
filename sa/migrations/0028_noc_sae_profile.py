# ----------------------------------------------------------------------
# no sae profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute(
            "UPDATE sa_managedobject SET name=%s,profile_name=%s WHERE name=%s",
            ["SAE", "NOC.SAE", "ROOT"],
        )
