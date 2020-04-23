# ----------------------------------------------------------------------
# vcdomain drop selector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("sa", "0072_managedobject_set_vcdomain")]

    def migrate(self):
        self.db.delete_column("vc_vcdomain", "selector_id")
