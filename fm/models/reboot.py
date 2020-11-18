# ---------------------------------------------------------------------
# Uptime report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging
from typing import Optional

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField, DateTimeField

# NOC modules
from noc.sa.models.managedobject import ManagedObject

logger = logging.getLogger(__name__)


class Reboot(Document):
    meta = {
        "collection": "noc.fm.reboots",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["ts", "object", ("object", "ts")],
    }

    object = IntField()
    ts = DateTimeField()  # Recovered time
    last = DateTimeField()  # Last up timestamp

    def __str__(self):
        return "%d" % self.object

    @classmethod
    def register(
        cls,
        managed_object: ManagedObject,
        ts: Optional[datetime.datetime] = None,
        last: Optional[datetime.datetime] = None,
    ):
        """
        Register reboot.
        Populated via Uptime.register(...)
        :param managed_object: Managed object reference
        :param ts: Recover time
        :param last: Last seen time
        """
        oid = managed_object.id
        ts = ts or datetime.datetime.now()
        last = last or ts
        logger.debug("[%s] Register reboot at %s", managed_object.name, ts)
        cls._get_collection().insert({"object": oid, "ts": ts, "last": last})
        if managed_object.object_profile.box_discovery_on_system_start:
            managed_object.run_discovery(
                delta=managed_object.object_profile.box_discovery_system_start_delay
            )
