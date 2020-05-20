# ----------------------------------------------------------------------
# ManagedObjectProfile ifdesc settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_ifdesc",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "ifdesc_patterns",
            DocumentReferenceField("inv.IfDescPatterns", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "ifdesc_handler",
            DocumentReferenceField("main.Handler", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile", "ifdesc_symmetric", models.BooleanField(default=False),
        )
