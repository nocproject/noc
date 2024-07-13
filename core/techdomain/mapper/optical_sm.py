# ----------------------------------------------------------------------
# OpticalSMMapper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from noc.inv.models.channel import Channel
from noc.core.channel.types import ChannelTopology
from .base import BaseMapper
from ..tracer.base import BaseTracer
from ..tracer.optical_dwdm import OpticalDWDMTracer


class OpticalSMMapper(BaseMapper):
    name = "optical_sm"

    def get_tracer(self) -> BaseTracer:
        if self.channel.topology == ChannelTopology.UBUNCH.value:
            return OpticalDWDMTracer()
        raise NotImplementedError()
