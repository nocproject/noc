# ----------------------------------------------------------------------
# Add VLAN field to ip.Prefix
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
# from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    depends_on = [("vc", "0029_migrate_vc_vlan")]

    def migrate(self):
        # Make legacy Address.state_id field nullable
        self.db.execute("ALTER TABLE ip_prefix DROP COLUMN vc_id")
        # Create new Address.state
        self.db.add_column(
            "ip_prefix", "vlan", DocumentReferenceField("vc.VLAN", null=True, blank=True)
        )
