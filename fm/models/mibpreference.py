# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIBPreference model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.lib.nosql as nosql


class MIBPreference(nosql.Document):
    meta = {
        "collection": "noc.mibpreferences",
        "allow_inheritance": False
    }
    mib = nosql.StringField(required=True, unique=True)
    preference = nosql.IntField(
        required=True, unique=True)  # The less is the better
    is_builtin = nosql.BooleanField(required=True, default=False)

    def __unicode__(self):
        return u"%s(%d)" % (self.mib, self.preference)
