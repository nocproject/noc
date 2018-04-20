# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Uptime report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField, DateTimeField
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

logger = logging.getLogger(__name__)


class Reboot(Document):
    meta = {
        "collection": "noc.fm.reboots",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
        "indexes": ["ts", "object", ("object", "ts")]
=======
        "indexes": ["object", ("object", "ts")]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
        managed_object.run_discovery(delta=300)
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
