# ----------------------------------------------------------------------
# Migrate ManagedObjectProfile MAC Discovery Policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        interface_profile_mac = [
            i
            for (i,) in self.db.execute(
                "SELECT id FROM sa_managedobjectprofile WHERE mac_collect_interface_profile = True"
            )
        ]
        self.db.delete_column("sa_managedobjectprofile", "mac_collect_all")
        self.db.delete_column("sa_managedobjectprofile", "mac_collect_interface_profile")
        self.db.delete_column("sa_managedobjectprofile", "mac_collect_management")
        self.db.delete_column("sa_managedobjectprofile", "mac_collect_multicast")
        self.db.delete_column("sa_managedobjectprofile", "mac_collect_vcfilter")
        self.db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_mac_filter_policy",
            models.CharField(
                "Box MAC Collect Policy",
                max_length=1,
                choices=[("I", "Interface Profile"), ("A", "All")],
                default="A",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "mac_collect_vlanfilter",
            DocumentReferenceField("vc.VLANFilter", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_mac_filter_policy",
            models.CharField(
                "Periodic MAC Collect Policy",
                max_length=1,
                choices=[("I", "Interface Profile"), ("A", "All")],
                default="A",
            ),
        )
        if interface_profile_mac:
            self.db.execute(
                """
                 UPDATE sa_managedobjectprofile
                 SET periodic_discovery_mac_filter_policy = 'I', box_discovery_mac_filter_policy = 'I'
                 WHERE id = ANY (%s)
                """,
                [interface_profile_mac],
            )
