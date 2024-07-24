# ----------------------------------------------------------------------
# OpticalDWDMControllerclass
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable, Optional, Tuple
from itertools import count

# NOC modules
from noc.inv.models.object import Object
from noc.core.channel.types import ChannelKind, ChannelTopology
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from .base import BaseController, Endpoint, PathItem


class OpticalDWDMController(BaseController):
    """
    Unidirectional p2p/bunch controller considering lambda.
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
                    break

    def iter_path(self, start: Endpoint) -> Iterable[PathItem]:
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
                    yield PathItem(object=ep.object, input=ep.name, output=oep.name)
                candidates.append(oep)
            for oep in candidates:
                # Next step trough cable
                pi = PathItem(object=ep.object, input=ep.name, output=oep.name)
                ep = self.get_peer(oep)
                if ep:
                    yield pi
                break
        self.logger.debug("Failed to trace")
        return None

    def sync_ad_hoc_channel(self, ep: Endpoint) -> Tuple[Optional[Channel], str]:
        """
        Create or update ad-hoc channel.

        Args:
            ep: Starting endpoint

        Returns:
            Channel instance, message
        """

        def next_free_pair() -> Optional[int]:
            """
            Generate next free pair number
            """
            if not self.use_pairs:
                return None
            while True:
                pn = next(pair_count)
                if pn not in used_pairs:
                    return pn

        obj = ep.object
        # Trace paths
        pairs = []
        resources = set()
        for sep in self.iter_endpoints(obj):
            eep = self.trace_path(sep)
            if not eep:
                continue
            pairs.append((sep, eep))
            resources.add(sep.as_resource())
            resources.add(eep.as_resource())
        # Find existing endpoints
        current_endpoints = {
            e.resource: e for e in DBEndpoint.objects.filter(resource__in=list(resources))
        }
        # Get channel or create new
        if current_endpoints:
            # Calculate number of channels
            cc = {x.channel for x in current_endpoints.values()}
            if len(cc) > 2:
                return None, "Multiple channels exists"
            channel = list(cc)[0]
            try:
                self.validate_ad_hoc_channel(channel)
            except ValueError as e:
                return None, str(e)
            used_pairs = {x.pair for x in current_endpoints.values() if x.pair}
        else:
            # Brand new channel
            channel = self.create_ad_hoc_channel()
            used_pairs = set()
        # Process endpoints
        pair_count = count(1)
        for sep, eep in pairs:
            start = current_endpoints.get(sep.as_resource())
            if not start:
                # Create start endpoint
                start = DBEndpoint(
                    channel=channel,
                    resource=sep.as_resource(),
                    is_root=self.is_unidirectional,
                    pair=next_free_pair() if self.use_pairs else None,
                )
                start.save()
            end = current_endpoints.get(eep.as_resource())
            if not end:
                end = DBEndpoint(
                    channel=channel,
                    resource=eep.as_resource(),
                    is_root=False,
                    pair=start.pair if self.use_pairs else None,
                )
                end.save()
        # @todo: Remove hanging endpoints
        if current_endpoints:
            return channel, "Channel updated"
        return channel, "Channel created"
