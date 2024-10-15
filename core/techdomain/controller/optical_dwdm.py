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
from noc.core.runner.models.jobreq import JobRequest
from ..profile.channel import ProfileChannelController
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
            for cc in ep.object.iter_effective_crossing():
                if cc.input == ep.name and cc.input_discriminator:
                    return cc.input_discriminator
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

        def iter_candidates(ep: Endpoint) -> Iterable[tuple[Endpoint, PathItem]]:
            for cc in ep.object.iter_cross(ep.name, [discriminator]):
                yield Endpoint(object=ep.object, name=cc.output), PathItem(
                    object=ep.object, input=ep.name, output=cc.output
                )

        def trace_path(ep: Endpoint) -> Iterable[PathItem]:
            r = []
            while True:
                pi = prev.get(ep)
                if not pi:
                    break
                r.append(pi)
                ep = Endpoint(object=pi.object, name=pi.input)
            yield from reversed(r)

        self.logger.info("Tracing from %s", start.label)
        discriminator = get_discriminator(start)
        if not discriminator:
            self.logger.info("No discriminator")
            return None
        self.logger.debug("Discriminator: %s", discriminator)

        queue = [start]
        prev: dict[Endpoint, PathItem] = {}
        while queue:
            ep = queue.pop(0)
            for oep, pi in iter_candidates(ep):
                if is_exit(oep):
                    self.logger.debug("Traced to %s", oep)
                    yield from trace_path(ep)
                    yield pi
                nep = self.get_peer(oep)
                if nep:
                    prev[nep] = pi
                    queue.append(nep)

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

        def get_job(
            ep: Endpoint, db_ep: DBEndpoint, destination: str | None = None
        ) -> JobRequest | None:
            label = ep.as_resource()
            self.logger.info("[%s] Getting profile controller for %s", label, ep.object)
            # Get cached
            if ep.object in pc_cache:
                ctl = pc_cache[ep.object]
            else:
                # Create controller
                ctl = ProfileChannelController.get_controller_for_object(ep.object, self.name)
                pc_cache[ep.object] = ctl
            if not ctl:
                self.logger.info("[%s] Controller is not supported, skipping", label)
                return None
            self.logger.info("[%s] Preparing setup", label)
            job = ctl.setup(db_ep, destination=destination)
            if job:
                if db_ep.is_root:
                    job.name = f"Set up entry of pair {db_ep.pair}"
                else:
                    job.name = f"Set up exit of pair {db_ep.pair}"
                db_ep.set_last_job(job.id)
            else:
                self.logger.info("[%s] Nothing to setup", label)
            return job

        pc_cache = {}
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
        jobs = []
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
            jobs.append(get_job(sep, start, destination=f"To {eep.label}"))
            end = current_endpoints.get(eep.as_resource())
            if not end:
                end = DBEndpoint(
                    channel=channel,
                    resource=eep.as_resource(),
                    is_root=False,
                    pair=start.pair if self.use_pairs else None,
                )
                end.save()
            jobs.append(get_job(eep, end, destination=f"From {sep.label}"))
        # Submit jobs
        jobs = [job for job in jobs if job]
        if jobs:
            job = JobRequest(name="Setup optical channel", jobs=jobs)
            job.submit()
        # @todo: Remove hanging endpoints
        if current_endpoints:
            return channel, "Channel updated"
        return channel, "Channel created"
