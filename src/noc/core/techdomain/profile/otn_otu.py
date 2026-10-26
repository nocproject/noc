# ----------------------------------------------------------------------
# BaseOTUProfileController
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from .channel import ProfileChannelController


class BaseOTUProfileController(ProfileChannelController):
    name = "otn_otu"
