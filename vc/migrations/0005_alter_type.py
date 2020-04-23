# ----------------------------------------------------------------------
# alter type
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.delete_column("vc_vc", "type_id")
        self.db.execute("ALTER TABLE vc_vcdomain ALTER COLUMN type_id SET NOT NULL")
