# ----------------------------------------------------------------------
# OTN OSC Controller for Horizon platform
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable

# from uuid import UUID

# NOC modules
from noc.core.runner.job import JobRequest
from noc.inv.models.endpoint import Endpoint
from noc.inv.models.object import Object
from noc.core.techdomain.profile.otn_osc import BaseOSCProfileController
from .base import ChannelMixin, SetValue


class Controller(BaseOSCProfileController, ChannelMixin):
    label = "OCS"
