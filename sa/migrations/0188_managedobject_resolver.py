# ----------------------------------------------------------------------
# ManagedObject resolver settings
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
        # ManagedObject profile
        self.db.delete_column("sa_managedobjectprofile", "sync_ipam")
        self.db.delete_column("sa_managedobjectprofile", "fqdn_template")
        self.db.add_column(
            "sa_managedobjectprofile",
            "fqdn_suffix",
            models.CharField("FQDN suffix", max_length=256, null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "address_resolution_policy",
            models.CharField(
                "Address Resolution Policy",
                choices=[("D", "Disabled"), ("O", "Once"), ("E", "Enabled")],
                max_length=1,
                null=False,
                blank=False,
                default="D",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "resolver_handler",
            DocumentReferenceField("main.Handler", null=True, blank=True),
        )
        # Managed Object
        self.db.add_column(
            "sa_managedobject",
            "fqdn",
            models.CharField("FQDN", max_length=256, null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobject",
            "address_resolution_policy",
            models.CharField(
                "Address Resolution Policy",
                choices=[("P", "Profile"), ("D", "Disabled"), ("O", "Once"), ("E", "Enabled")],
                max_length=1,
                null=False,
                blank=False,
                default="P",
            ),
        )
