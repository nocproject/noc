# ----------------------------------------------------------------------
# OpticalDWDMTracer class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable, Optional, Tuple

# NOC modules
from noc.inv.models.object import Object
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from noc.inv.models.techdomain import TechDomain
from noc.core.channel.types import ChannelKind, ChannelTopology
from .base import BaseTracer, Endpoint


class OpticalDWDMTracer(BaseTracer):
    """
    Unidirectional p2p/bunch tracer considering lambda.
    """

    name = "optical_dwdm"
    kind = ChannelKind.L1
    topology = ChannelTopology.UBUNCH
    tech_domain = "optical_sm"

    def iter_endpoints(self, obj: Object) -> Iterable[Endpoint]:
        for c in obj.model.connections:
            if not c.protocols:
                continue
            for pvi in c.protocols:
                if pvi.protocol.code == "DWDM" and pvi.direction == ">" and pvi.discriminator:
                    yield Endpoint(object=obj, name=c.name)

    def trace_path(self, start: Endpoint) -> Optional[Endpoint]:
        def get_discriminator(ep: Endpoint) -> Optional[str]:
            for item in self.iter_cross(ep.object):
                if item.input == ep.name and item.input_discriminator:
                    return item.input_discriminator
            return None

        def is_exit(ep: Endpoint) -> bool:
            """
            Check if endpoint is an appropriate exit.
            """
            for c in ep.object.model.connections:
                if c.name != ep.name:
                    continue
                if not c.protocols:
                    return False
                for pvi in c.protocols:
                    if pvi.protocol.code == "DWDM" and pvi.direction == "<" and pvi.discriminator:
                        return True
                return False
            return False

        self.logger.info("Tracing from %s", start)
        discriminator = get_discriminator(start)
        if not discriminator:
            self.logger.info("No discriminator")
            return None
        self.logger.debug("Discriminator: %s", discriminator)
        ep = start
        while ep:
            self.logger.debug("Tracing %s", ep)
            # From input to output
            candidates = []  # We may found real exit on next step
            for out in ep.object.iter_cross(ep.name, [discriminator]):
                # Check if output is satisfactory
                oep = Endpoint(object=ep.object, name=out)
                if is_exit(oep):
                    self.logger.debug("Traced to %s", oep)
                    return oep
                candidates.append(oep)
            for oep in candidates:
                # Next step trough cable
                ep = self.get_peer(oep)
                break
        self.logger.debug("Failed to trace")
        return None
