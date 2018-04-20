# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# MIBData model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## MIBData model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import noc.lib.nosql as nosql
from mib import MIB


class MIBData(nosql.Document):
    meta = {
        "collection": "noc.mibdata",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "indexes": ["oid", "name", "mib", "aliases"]
    }
    mib = nosql.PlainReferenceField(MIB)
    oid = nosql.StringField(required=True, unique=True)
    name = nosql.StringField(required=True)
    description = nosql.StringField(required=False)
    syntax = nosql.DictField(required=False)
    aliases = nosql.ListField(nosql.StringField(), default=[])

    def __unicode__(self):
        return self.name
