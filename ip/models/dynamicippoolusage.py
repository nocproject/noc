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
        "indexes": [("termination_group", "vrf", "pool_name", "technology")]
    }

    termination_group = ForeignKeyField(TerminationGroup)
    vrf = ForeignKeyField(VRF)
    pool_name = StringField()
    technology = StringField()
    usage = IntField()

    def __unicode__(self):
        return u"%s %s" % (self.termination_group.name, self.pool_name)

    @classmethod
    def register_usage(cls, termination_group, vrf=None,
                       pool_name="default", technology="IPoE"):
        """
        Increase usage counter
        """
        if not vrf:
            vrf = VRF.get_global()
        cls._get_collection().update(
            {
                "termination_group": termination_group.id,
                "vrf": vrf.id,
                "pool_name": pool_name,
                "technology": technology
            }, {
                "$inc": {
                    "usage": 1
                }
            },
            upsert=True
        )

    @classmethod
    def unregister_usage(cls, termination_group, vrf=None,
                       pool_name="default", technology="IPoE"):
        """
        Decrease usage counter
        """
        if not vrf:
            vrf = VRF.get_global()
        cls._get_collection().update(
            {
                "termination_group": termination_group.id,
                "vrf": vrf.id,
                "pool_name": pool_name,
                "technology": technology
            }, {
                "$inc": {
                    "usage": -1
                }
            },
            upsert=True
        )

    @classmethod
    def get_usage(cls, termination_group, vrf=None,
                       pool_name="default", technology="IPoE"):
        if not vrf:
            vrf = VRF.get_global()
        r = cls._get_collection().find_one(
            {
                "termination_group": termination_group.id,
                "vrf": vrf.id,
                "pool_name": pool_name,
                "technology": technology
            },
            {"usage": 1}
        )
        if r:
            return r["usage"]
        else:
            return 0
