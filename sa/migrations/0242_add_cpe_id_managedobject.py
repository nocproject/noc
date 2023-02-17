# ----------------------------------------------------------------------
# Add cpe_id field to ManagedObject
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobject",
            "cpe_id",
            DocumentReferenceField("inv.CPE", null=True, blank=True),
        )
        # Delete ManagedObject CPE
        self.db.delete_column("sa_managedobject", "local_cpe_id")
        self.db.delete_column("sa_managedobject", "global_cpe_id")
        self.db.delete_column("sa_managedobject", "last_seen")
        # Delete ManagedObject Profile CPE Options
        self.db.delete_column("sa_managedobjectprofile", "cpe_segment_policy")
        self.db.delete_column("sa_managedobjectprofile", "cpe_cooldown")
        self.db.delete_column("sa_managedobjectprofile", "cpe_profile_id")
        self.db.delete_column("sa_managedobjectprofile", "cpe_auth_profile_id")
        self.db.delete_column("sa_managedobjectprofile", "enable_box_discovery_cpestatus")
