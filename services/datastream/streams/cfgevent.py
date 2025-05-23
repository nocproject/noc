# ----------------------------------------------------------------------
# cfgevent
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# NOC modules
from noc.core.datastream.base import DataStream
from noc.fm.models.eventclass import EventClass


class CfgEventDataStream(DataStream):
    name = "cfgevent"

    @classmethod
    def get_object(cls, oid: str) -> Dict[str, Any]:
        oid = str(oid)
        if oid.startswith("ec:"):
            event_class = EventClass.get_by_id(oid[3:])
        else:
            event_class = EventClass.get_by_id(oid)
        if not event_class:
            raise KeyError()
        r = EventClass.get_event_config(event_class)
        r["id"] = str(event_class.id)
        return r
