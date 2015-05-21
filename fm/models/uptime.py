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
from noc.lib.nosql import (Document, IntField, DateTimeField, FloatField)
from reboot import Reboot
from noc.lib.dateutils import total_seconds

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
    last_value = FloatField()  # Last registred value

    SEC = datetime.timedelta(seconds=1)
    FWRAP = float((1 << 32) - 1) / 100.0
    WRAP = datetime.timedelta(seconds=FWRAP)
    WPREC = 0.1  # Wrap precision

    def __unicode__(self):
        return u"%d" % self.object

    @classmethod
    def is_reboot(cls, old_uptime, new_uptime):
        """
        Returns true if reboot detected
        :param old_uptime:
        :param new_uptime:
        :return:
        """
        if old_uptime > new_uptime:
            # Check for counter wrap
            return True
        return False

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
        delta = datetime.timedelta(seconds=uptime)
        logger.debug("[%s] Register uptime %s",
                     managed_object.name, delta)
        # Update data
        c = cls._get_collection()
        d = c.find_one({
            "object": oid,
            "stop": None
        })
        if d:
            # Check for reboot
            is_rebooted = False
            if d["last_value"] > uptime:
                # Check for counter wrapping
                # Get wrapped delta
                dl = cls.FWRAP - d["last_value"] + uptime
                # Get timestamp delta
                tsd = total_seconds(now - d["last"])
                if abs(dl - tsd) > tsd * cls.WPREC:
                    is_rebooted = True
                else:
                    logger.debug("Counter wrap detected")
            if is_rebooted:
                # Reboot registered
                # Closing existing uptime
                ts = now - delta
                logger.debug("[%s] Closing uptime (%s - %s, delta %s)",
                             managed_object.name,
                             d["start"], ts - cls.SEC,
                             delta)
                c.update(
                    {"_id": d["_id"]},
                    {
                        "$set": {
                            "stop": ts - cls.SEC
                        }
                    }
                )
                # Start new uptime
                logger.debug("[%s] Starting new uptime from %s",
                             managed_object.name, ts)
                c.insert({
                    "object": oid,
                    "start": ts,
                    "stop": None,
                    "last": now,
                    "last_value": uptime
                })
                #
                Reboot.register(managed_object, ts, d["last"])
            else:
                logger.debug(
                    "[%s] Refreshing existing uptime (%s - %s)",
                    managed_object.name,
                    d["start"], now
                )
                c.update(
                    {"_id": d["_id"]},
                    {
                        "$set": {
                            "last": now,
                            "last_value": uptime
                        }
                    }
                )
        else:
            # First uptime
            logger.debug("[%s] First uptime from %s",
                         managed_object.name, now)
            c.insert({
                "object": oid,
                "start": now - delta,
                "stop": None,
                "last": now,
                "last_value": uptime
            })
