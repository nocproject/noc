# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# VC.project
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
=======
##----------------------------------------------------------------------
## VC.project
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from south.db import db
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        c = get_db()["noc.sync"]
        smap = {}  # name -> id
        for d in c.find():
            smap[d["name"]] = str(d["_id"])
        # Create .sync
        db.execute("ALTER TABLE dns_dnsserver ADD sync CHAR(24)")
        for i, ch in db.execute("SELECT id, sync_channel FROM dns_dnsserver WHERE sync_channel IS NOT NULL"):
            if ch not in smap:
                n = c.insert({
                    "name": ch,
                    "is_active": True,
                    "description": "Converted from DNS Server settings"
                })
                smap[ch] = str(n)
            print smap
            db.execute("UPDATE dns_dnsserver SET sync=%s WHERE id=%s", [smap[ch], i])
        db.drop_column("dns_dnsserver", "sync_channel")

    def backwards(self):
        db.drop_column("dns_dnsserver", "sync")
