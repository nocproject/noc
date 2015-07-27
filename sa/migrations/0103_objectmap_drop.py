# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC models
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        get_db().noc.cache.object_map.drop()

    def backwards(self):
        pass