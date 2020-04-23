# ----------------------------------------------------------------------
# ManagedObject ResourceGroup integration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import ObjectIDArrayField


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobject",
            "static_service_groups",
            ObjectIDArrayField(db_index=True, default="{}"),
        )
        self.db.add_column(
            "sa_managedobject",
            "effective_service_groups",
            ObjectIDArrayField(db_index=True, default="{}"),
        )
        self.db.add_column(
            "sa_managedobject",
            "static_client_groups",
            ObjectIDArrayField(db_index=True, default="{}"),
        )
        self.db.add_column(
            "sa_managedobject",
            "effective_client_groups",
            ObjectIDArrayField(db_index=True, default="{}"),
        )
