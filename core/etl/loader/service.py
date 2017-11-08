# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.models.service import Service

## NOC modules
from base import BaseLoader


class ServiceLoader(BaseLoader):
    """
    Service loader
    """
    name = "service"
    model = Service
    fields = [
        "id",
        "parent",
        "subscriber",
        "profile",
        "ts",
        "logical_status",
        "logical_status_start",
        "agreement_id",
        "order_id",
        "stage_id",
        "stage_name",
        "stage_start",
        "account_id",
        "address",
        "managed_object",
        "nri_port",
        "cpe_serial",
        "cpe_mac",
        "cpe_model",
        "cpe_group",
        "description"
    ]

    mapped_fields = {
        "parent": "service",
        "subscriber": "subscriber",
        "profile": "serviceprofile",
        "managed_object": "managedobject"
    }

    discard_deferred = True
