# ----------------------------------------------------------------------
# IP Address Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.ipaddress import IPAddress
from noc.ip.models.address import Address


class IPAddressLoader(BaseLoader):
    """
    IP Address loader
    """

    name = "ipaddress"
    model = Address
    data_model = IPAddress
    ignore_unique = {"bi_id", "ipv6_transition"}

    workflow_delete_event = "remove"
    workflow_state_sync = True
