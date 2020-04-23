# ----------------------------------------------------------------------
# ManagedObjectSelector.filter_service_group and .filter_client_group
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_service_group",
            DocumentReferenceField("inv.ResourceGroup", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_client_group",
            DocumentReferenceField("inv.ResourceGroup", null=True, blank=True),
        )
