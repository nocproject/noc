# ----------------------------------------------------------------------
# Migrate ManagedObject's/Profile's handlers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import bson
from pymongo import InsertOne, DeleteOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0054_migrate_pyrule")]

    def migrate(self):
        # Managed Object Profile
        self.migrate_handler_ids()
        self.migrate_handler("sa_managedobjectprofile", "hk_handler", allow_housekeeping=True)
        # Managed Object
        self.migrate_handler("sa_managedobject", "config_filter_handler", allow_config_filter=True)
        self.migrate_handler(
            "sa_managedobject", "config_diff_filter_handler", allow_config_diff_filter=True
        )
        self.migrate_handler(
            "sa_managedobject", "config_validation_handler", allow_config_validation=True
        )

    def migrate_handler_ids(self):
        h_coll = self.mongo_db["handlers"]
        bulk = []
        for doc in h_coll.find({}):
            doc["handler"] = doc["_id"]
            doc["_id"] = bson.ObjectId()
            bulk += [InsertOne(doc), DeleteOne({"_id": doc["handler"]})]
            self.db.execute(
                """
                UPDATE sa_managedobjectprofile
                SET resolver_handler = %s
                WHERE resolver_handler = %s
                """,
                [str(doc["_id"]), doc["handler"]],
            )
        if bulk:
            h_coll.bulk_write(bulk, ordered=True)

    def migrate_handler(self, table, field, **kwargs):
        h_coll = self.mongo_db["handlers"]
        for mop_id, handler in self.db.execute(
            """
            SELECT id, %s
            FROM %s
            WHERE %s IS NOT NULL
            """
            % (field, table, field)
        ):
            # Create handler
            h_id = bson.ObjectId()
            h_data = {
                "_id": h_id,
                "handler": handler,
                "name": handler,
                "description": "Migrated %s's %s %s" % (table, field, handler),
            }
            h_data.update(kwargs)
            h_coll.insert_one(h_data)
            # Migrate profile
            self.db.execute(
                """
                UPDATE %s
                SET %s = %%s
                WHERE %s = %%s
                """
                % (table, field, field),
                [str(h_id), handler],
            )
        self.db.execute("ALTER TABLE %s ALTER COLUMN %s TYPE CHAR(24)" % (table, field))
