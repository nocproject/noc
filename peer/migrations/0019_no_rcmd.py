# ----------------------------------------------------------------------
# no rcmd
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.delete_column("peer_peeringpoint", "lg_rcmd")
        self.db.delete_column("peer_peeringpoint", "provision_rcmd")
