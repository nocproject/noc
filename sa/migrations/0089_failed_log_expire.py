# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        expires = datetime.datetime.now() + datetime.timedelta(days=7)
        c = get_db()["noc.log.sa.failed_scripts"]
        c.update_many({}, {
            "$set": {
                "expires": expires
            }
        })

    def backwards(self):
        pass
