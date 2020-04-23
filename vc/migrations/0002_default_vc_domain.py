# ---------------------------------------------------------------------
# Create "default" VC domain, if not exists
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        if (
            self.db.execute("SELECT COUNT(*) FROM vc_vcdomain WHERE name=%s", ["default"])[0][0]
            == 0
        ):
            self.db.execute(
                "INSERT INTO vc_vcdomain(name,description) VALUES(%s,%s)",
                ["default", "Default VC Domain"],
            )
