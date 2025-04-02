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
from noc.fm.models.eventcategory import EventCategory


class CfgEventDataStream(DataStream):
    name = "cfgevent"

    @classmethod
    def get_object(cls, oid: str) -> Dict[str, Any]:
        oid = str(oid)
        if oid.startswith("ec:"):
            ec = EventClass.get_by_id(oid[3:])
        elif oid.startswith("c:"):
            ec = EventCategory.get_by_id(oid[2:])
        else:
            ec = EventClass.get_by_id(oid)
            # For datastream rebuild
            if not ec:
                ec = EventCategory.get_by_id(oid)
        if not ec:
            raise KeyError()
        r = ec.get_event_config(ec)
        r["id"] = str(ec.id)
        return r
