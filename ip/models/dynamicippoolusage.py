# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dynamic IPPool Usage
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField
## NOC modules
from noc.sa.models.terminationgroup import TerminationGroup
from noc.ip.models.vrf import VRF
from noc.lib.nosql import ForeignKeyField


class DynamicIPPoolUsage(Document):
    meta = {
        "collection": "noc.dynamic_ippool_isage",
        "allow_inheritance": False,
        "indexes": [("termination_group", "vrf", "name")]
    }

    termination_group = ForeignKeyField(TerminationGroup)
    vrf = ForeignKeyField(VRF)
    pool_name = StringField()
    usage = IntField()

    def __unicode__(self):
        return u"%s %s" % (self.termination_group.name, self.pool_name)

    @classmethod
    def register_usage(self, termination_group, vrf=None, name="default"):
        if not vrf:
            vrf = VRF.get_global()
