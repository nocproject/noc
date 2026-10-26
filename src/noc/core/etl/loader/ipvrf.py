# ----------------------------------------------------------------------
# IP VRF Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.ip.models.vrf import VRF

from ..models.ipvrf import IPVRF
from .base import BaseLoader


class IPVRFLoader(BaseLoader):
    """
    IP VRF loader
    """

    name = "ipvrf"
    model = VRF
    data_model = IPVRF

    workflow_delete_event = "remove"
    workflow_state_sync = True
