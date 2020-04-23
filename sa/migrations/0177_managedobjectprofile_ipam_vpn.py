# ----------------------------------------------------------------------
# VPN discovery settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute(
            """
          ALTER TABLE sa_managedobjectprofile
          RENAME enable_box_discovery_vrf
          TO enable_box_discovery_vpn_interface"""
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_vpn_mpls",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "vpn_profile_interface",
            DocumentReferenceField("vc.VPNProfile", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "vpn_profile_mpls",
            DocumentReferenceField("vc.VPNProfile", null=True, blank=True),
        )
