# ----------------------------------------------------------------------
# Remove Selector field from Objectnotification, Commandsnippet models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [
        ("sa", "0218_command_snippet_obj_notification_resource_group"),
        ("sa", "0219_managed_object_selector_resource_group"),
    ]

    def migrate(self):
        # MAP Resource Group to Selector by name
        rg_coll = self.mongo_db["resourcegroups"]
        rg_name = {}
        for rg in rg_coll.find():
            rg_name[rg["name"]] = str(rg["_id"])
        selector_rg_map = {}
        for s_id, name in self.db.execute("SELECT id, name FROM sa_managedobjectselector"):
            if not s_id:
                continue
            name = f"MOS {name}"
            if name not in rg_name:
                print("Not found selector")
                continue
            selector_rg_map[s_id] = rg_name[name]
        for table in ("sa_objectnotification", "sa_commandsnippet"):
            for (s_id,) in self.db.execute(f"SELECT DISTINCT(selector_id) FROM {table}"):
                # Append to resource groups AS services
                self.db.execute(
                    f"UPDATE {table} SET resource_group = %s WHERE selector_id = %s",
                    [selector_rg_map[s_id], s_id],
                )
            # Set profile as not null
            self.db.execute(f"ALTER TABLE {table} ALTER resource_group SET NOT NULL")
            # Delete column
            self.db.delete_column(
                table,
                "selector_id",
            )
        for table in (
            "sa_useraccess",
            "sa_groupaccess",
        ):
            # Delete column
            self.db.delete_column(
                table,
                "selector_id",
            )
