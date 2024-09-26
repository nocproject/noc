# ----------------------------------------------------------------------
# OTN OSC Controller for Horizon platform
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.techdomain.profile.otn_osc import BaseOSCProfileController
from .base import ChannelMixin


class Controller(BaseOSCProfileController, ChannelMixin):
    label = "OCS"
