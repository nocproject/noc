# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TTMap loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseLoader
from noc.inv.models.extnrittmap import ExtNRITTMap


class TTMapLoader(BaseLoader):
    name = "ttmap"
    model = ExtNRITTMap
    discard_deferred = True
    fields = [
        "id",
        "managed_object",
        "tt_system",
        "queue",
        "remote_id"
    ]

    mapped_fields = {
        "managed_object": "managedobject",
        "tt_system": "ttsystem"
    }
