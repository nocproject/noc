# ----------------------------------------------------------------------
# BaseOSCProfileController
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .channel import ProfileChannelController


class BaseOSCProfileController(ProfileChannelController):
    name = "otn_osc"
