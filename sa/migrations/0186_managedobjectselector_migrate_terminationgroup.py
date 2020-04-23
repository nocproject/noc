# ----------------------------------------------------------------------
# Migrate ManagedObject Termination Groups to Resource Groups
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        c_ids = [
            x[0]
            for x in self.db.execute(
                "SELECT DISTINCT filter_termination_group_id "
                "FROM sa_managedobjectselector "
                "WHERE filter_termination_group_id IS NOT NULL"
            )
        ]
        s_ids = [
            x[0]
            for x in self.db.execute(
                "SELECT DISTINCT filter_service_terminator_id "
                "FROM sa_managedobjectselector "
                "WHERE filter_service_terminator_id IS NOT NULL"
            )
        ]
        mdb = self.mongo_db
        rg_map = {
            x["_legacy_id"]: str(x["_id"])
            for x in mdb.resourcegroups.find(
                {"_legacy_id": {"$exists": True}}, {"_id": 1, "_legacy_id": 1}
            )
        }
        # Append to resource groups AS clients
        for tg_id in c_ids:
            self.db.execute(
                "UPDATE sa_managedobjectselector "
                "SET "
                "  filter_client_group = %s "
                "WHERE filter_termination_group_id = %s",
                [rg_map[tg_id], tg_id],
            )
        # Append to resource groups AS services
        for tg_id in s_ids:
            self.db.execute(
                "UPDATE sa_managedobjectselector "
                "SET "
                "  filter_service_group = %s "
                "WHERE filter_service_terminator_id = %s",
                [rg_map[tg_id], tg_id],
            )
        # Finally remove columns
        self.db.delete_column("sa_managedobjectselector", "filter_termination_group_id")
        self.db.delete_column("sa_managedobjectselector", "filter_service_terminator_id")
