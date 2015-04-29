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
from reboot import Reboot

logger = logging.getLogger(__name__)


class Uptime(Document):
    meta = {
        "collection": "noc.fm.uptimes",
        "indexes": ["object", ("object", "stop")]
    }

    object = IntField()
    start = DateTimeField()
    stop = DateTimeField()  # None for active uptime
    last = DateTimeField()  # Last update

    EPSILON = datetime.timedelta(seconds=3)
    SEC = datetime.timedelta(seconds=1)

    def __unicode__(self):
        return u"%d" % self.object

    @classmethod
    def register(cls, managed_object, uptime):
        """
        Register uptime
        :param managed_object: Managed object reference
        :param uptime: Registered uptime in seconds
        """
        if not uptime:
            return
        oid = managed_object.id
        now = datetime.datetime.now()
        delta = datetime.timedelta(milliseconds=int(uptime * 1000))
        logger.debug("[%s] Register uptime %s",
                     managed_object.name, delta)
        # Update data
        c = cls._get_collection()
        d = c.find_one({
            "object": oid,
            "stop": None
        })
        if d:
            r_uptime = now - d["start"]
            if r_uptime - delta > cls.EPSILON:
                logger.debug("[%s] Reboot registered",
                             managed_object.name)
                # Reboot registered
                # @todo: Fix counter wrapping
                ts = now - delta
                c.update(
                    {"_id": d["_id"]},
                    {
                        "$set": {
                            "stop": ts - cls.SEC,
                            "last": now
                        }
                    }
                )
                logger.debug("[%s] Starting new uptime",
                             managed_object.name)
                c.insert({
                    "object": oid,
                    "start": ts,
                    "stop": None,
                    "last": now
                })
                #
                Reboot.register(managed_object, ts, d["last"])
            else:
                c.update(
                    {"_id": d["_id"]},
                    {
                        "$set": {
                            "last": now
                        }
                    }
                )
        else:
            # First uptime
            logger.debug("[%s] First uptime", managed_object.name)
            c.insert({
                "object": oid,
                "start": now - delta,
                "stop": None,
                "last": now
            })
