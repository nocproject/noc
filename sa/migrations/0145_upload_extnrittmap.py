# ----------------------------------------------------------------------
# upload extnrittmap
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        collection = self.mongo_db["noc.extnrittmap"]
        mappings = [
            (d["managed_object"], str(d["tt_system"]), str(d["queue"]), str(d["remote_id"]))
            for d in collection.find()
        ]
        for mo, tts, ttqueue, ttid in mappings:
            self.db.execute(
                """UPDATE sa_managedobject
                SET tt_system = %s,
                    tt_queue = %s,
                    tt_system_id = %s
                WHERE id = %s""",
                [tts, ttqueue, ttid, mo],
            )
