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
        "source",
        "src_mo",
        "src_interface",
        "dst_mo",
        "dst_interface"
    ]

    mapped_fields = {
        "src_mo": "managedobject",
        "dst_mo": "managedobject"
    }

    discard_deferred = True
