# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Migrate KB Bookmarks to Favorites
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
import six
# Third-party modules
from south.db import db
# NOC modules
from noc.lib.nosql import get_db


class Migration(object):

    def forwards(self):
        favs = defaultdict(list)
        mdb = get_db()
        fav_coll = mdb["noc.favorites"]
        global_bookmarks = [x[0] for x in db.execute("SELECT kb_entry_id FROM kb_kbglobalbookmark")]
        user_bookmarks = db.execute("SELECT user_id, kb_entry_id FROM kb_kbuserbookmark")
        for user, kb_entry in user_bookmarks:
            favs[user] += [kb_entry]
        if favs:
            for u, fav in six.iteritems(favs):
                print({"user": u, "app": "kb.kbentry", "favorite_app": False, "favorites": fav})
                fav_coll.insert_one({"user": u, "app": "kb.kbentry", "favorite_app": False,
                                     "favorites": fav + global_bookmarks})

    def backward(self):
        pass
