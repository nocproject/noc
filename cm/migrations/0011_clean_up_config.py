# ----------------------------------------------------------------------
# clean config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("sa", "0008_copy_objects")]

    def migrate(self):
        # self.db.execute("DROP INDEX cm_config_managed_object_id")
        # self.db.execute("CREATE UNIQUE INDEX cm_config_managed_object_id ON cm_config(managed_object_id)")
        self.db.delete_column("cm_objectnotify", "category_id")
        self.db.delete_column("cm_objectnotify", "location_id")
        for column in [
            "activator_id",
            "profile_name",
            "scheme",
            "address",
            "port",
            "user",
            "password",
            "super_password",
            "remote_path",
            "trap_source_ip",
            "trap_community",
        ]:
            self.db.delete_column("cm_config", column)
        for table in ["cm_config", "cm_rpsl", "cm_dns", "cm_prefixlist"]:
            self.db.delete_column(table, "location_id")
            self.db.delete_table("%s_categories" % table)
        self.db.delete_table("cm_object_categories")
        self.db.delete_table("cm_objectaccess")
        self.db.execute("DELETE FROM cm_objectcategory")
        self.db.delete_table("cm_objectcategory")
        self.db.delete_table("cm_objectlocation")
