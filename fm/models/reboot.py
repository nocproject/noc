# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Uptime report
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import logging
## NOC modules
from noc.lib.nosql import (Document, IntField, DateTimeField)

logger = logging.getLogger(__name__)


class Reboot(Document):
    meta = {
        "collection": "noc.fm.reboots",
        "indexes": ["object", ("object", "ts")]
    }

    object = IntField()
    ts = DateTimeField()  # Recovered time
    last = DateTimeField()  # Last up timestamp

    def __unicode__(self):
        return u"%d" % self.object

    @classmethod
    def register(cls, managed_object, ts=None, last=None):
        """
        Register reboot.
        Populated via Uptime.register(...)
        :param managed_object: Managed object reference
        :param ts: Recover time
        :params last: Last seen time
        """
        oid = managed_object.id
        if not ts:
            ts = datetime.datetime.now()
        if not last:
            last = ts
        logger.debug("[%s] Register reboot at %s",
                     managed_object.name, ts)
        cls._get_collection().insert({
            "object": oid,
            "ts": ts,
            "last": last
        })
