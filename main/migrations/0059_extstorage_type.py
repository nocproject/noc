# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ExtStorage.type
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        db = get_db()
        coll = db["extstorages"]
        coll.update_many({
            "enable_config_mirror": True
        }, {
            "$set": {
                "type": "config_mirror"
            }
        })
        coll.update_many({
            "enable_beef": True
        }, {
            "$set": {
                "type": "beef"
            }
        })

    def backwards(self):
        pass
