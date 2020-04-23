# ----------------------------------------------------------------------
# Migrate KB Bookmarks to Favorites
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        favs = defaultdict(list)
        mdb = self.mongo_db
        fav_coll = mdb["noc.favorites"]
        global_bookmarks = [
            x[0] for x in self.db.execute("SELECT kb_entry_id FROM kb_kbglobalbookmark")
        ]
        user_bookmarks = self.db.execute("SELECT user_id, kb_entry_id FROM kb_kbuserbookmark")
        for user, kb_entry in user_bookmarks:
            favs[user] += [kb_entry]
        if favs:
            for u, fav in favs.items():
                fav_coll.insert_one(
                    {
                        "user": u,
                        "app": "kb.kbentry",
                        "favorite_app": False,
                        "favorites": fav + global_bookmarks,
                    }
                )
