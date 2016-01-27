# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Link loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseLoader
from noc.inv.models.extnrilink import ExtNRILink


class LinkLoader(BaseLoader):
    """
    Managed Object loader
    """
    name = "link"
    model = ExtNRILink
    fields = [
        "id",
        "src_mo",
        "src_chassis",
        "src_slot",
        "src_port",
        "dst_mo",
        "dst_chassis",
        "dst_slot",
        "dst_port",
    ]

    mapped_fields = {
        "src_mo": "managedobject",
        "dst_mo": "managedobject"
    }

    discard_deferred = True