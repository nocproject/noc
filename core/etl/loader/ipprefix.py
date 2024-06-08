# ----------------------------------------------------------------------
# IP VRF Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.ipprefix import IPPrefix
from noc.ip.models.prefix import Prefix


class IPPrefixLoader(BaseLoader):
    """
    IP Prefix Loader
    """

    name = "ipprefix"
    model = Prefix
    data_model = IPPrefix
    ignore_unique = {"bi_id", "ipv6_transition"}

    workflow_delete_event = "remove"
    workflow_state_sync = True
