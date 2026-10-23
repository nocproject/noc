# ----------------------------------------------------------------------
# BaseODUProfileController
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .channel import ProfileChannelController


class BaseODUProfileController(ProfileChannelController):
    name = "otn_odu"
