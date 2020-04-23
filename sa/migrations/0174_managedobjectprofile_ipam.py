# ----------------------------------------------------------------------
# managedobjectprofile ipam
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
    depends_on = [("ip", "0038_address_name"), ("main", "0037_template")]

    def migrate(self):
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_address_management",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_address_dhcp",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "address_profile_interface",
            DocumentReferenceField("ip.AddressProfile", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "address_profile_management",
            DocumentReferenceField("ip.AddressProfile", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "address_profile_neighbor",
            DocumentReferenceField("ip.AddressProfile", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "address_profile_dhcp",
            DocumentReferenceField("ip.AddressProfile", null=True, blank=True),
        )
