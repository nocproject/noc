# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Initialize inventory hierarchy
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        db = get_db()
        # Initialize container models
        collection = db.noc.networksegments

        if collection.count() == 0:
            print "    Create default network segment"
            collection.insert({
                "name": "ALL",
                "parent": None,
                "description": "All network",
                "settings": {}
            })

    def backwards(self):
        pass
