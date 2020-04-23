# ----------------------------------------------------------------------
# ManagedObject and ManagedObjectProfile ConfDB discovery settings
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
        # ManagedObjectProfile
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_address_confdb",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_prefix_confdb",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_vpn_confdb",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "address_profile_confdb",
            DocumentReferenceField("ip.PrefixProfile", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "prefix_profile_confdb",
            DocumentReferenceField("ip.PrefixProfile", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "vpn_profile_confdb",
            DocumentReferenceField("vc.VPNProfile", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "interface_discovery_policy",
            models.CharField(
                "Interface Discovery Policy",
                max_length=1,
                choices=[
                    ("s", "Script"),
                    ("S", "Script, ConfDB"),
                    ("C", "ConfDB, Script"),
                    ("c", "ConfDB"),
                ],
                default="s",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "caps_discovery_policy",
            models.CharField(
                "Caps Discovery Policy",
                max_length=1,
                choices=[
                    ("s", "Script"),
                    ("S", "Script, ConfDB"),
                    ("C", "ConfDB, Script"),
                    ("c", "ConfDB"),
                ],
                default="s",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "vlan_discovery_policy",
            models.CharField(
                "VLAN Discovery Policy",
                max_length=1,
                choices=[
                    ("s", "Script"),
                    ("S", "Script, ConfDB"),
                    ("C", "ConfDB, Script"),
                    ("c", "ConfDB"),
                ],
                default="s",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "interface_discovery_policy",
            models.CharField(
                "Interface Discovery Policy",
                max_length=1,
                choices=[
                    ("P", "From Profile"),
                    ("s", "Script"),
                    ("S", "Script, ConfDB"),
                    ("C", "ConfDB, Script"),
                    ("c", "ConfDB"),
                ],
                default="P",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "caps_discovery_policy",
            models.CharField(
                "Caps Discovery Policy",
                max_length=1,
                choices=[
                    ("P", "From Profile"),
                    ("s", "Script"),
                    ("S", "Script, ConfDB"),
                    ("C", "ConfDB, Script"),
                    ("c", "ConfDB"),
                ],
                default="P",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "vlan_discovery_policy",
            models.CharField(
                "VLAN Discovery Policy",
                max_length=1,
                choices=[
                    ("P", "From Profile"),
                    ("s", "Script"),
                    ("S", "Script, ConfDB"),
                    ("C", "ConfDB, Script"),
                    ("c", "ConfDB"),
                ],
                default="P",
            ),
        )
