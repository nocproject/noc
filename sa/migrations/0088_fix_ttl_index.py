# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

##
from noc.lib.nosql import get_db

class Migration:
    def forwards(self):
        db = get_db()
        c = get_db()["noc.log.sa.interaction"]
        c.drop_index("expire_1")

    def backwards(self):
        pass
