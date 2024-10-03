# ----------------------------------------------------------------------
# OTNOSCController class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable, Tuple

# NOC modules
from noc.inv.models.object import Object
from noc.core.channel.types import ChannelKind, ChannelTopology
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from noc.core.runner.models.jobreq import JobRequest
from ..profile.channel import ProfileChannelController
from .base import BaseController, Endpoint, PathItem


class OTNOSCController(BaseController):
    """
    OTN OSC level controller
    """

    name = "otn_osc"
    kind = ChannelKind.L1
    topology = ChannelTopology.UP2P
    tech_domain = "otn_osc"
    adhoc_bidirectional = False
    adhoc_endpoints = True
    DISCRIMINATOR = "osc::outband"

    def iter_endpoints(self, obj: Object) -> Iterable[Endpoint]:
        for c in obj.model.connections:
            if not c.protocols:
                continue
            for pvi in c.protocols:
                if pvi.protocol.code == "OSC" and pvi.direction == ">":
                    yield Endpoint(object=obj, name=c.name)
                    break

    def iter_path(self, start: Endpoint) -> Iterable[PathItem]:
        def pass_crossing(ep: Endpoint) -> Endpoint | None:
            for cc in ep.object.iter_cross(ep.name, [self.DISCRIMINATOR]):
                if cc.input_discriminator == self.DISCRIMINATOR:
                    return Endpoint(object=ep.object, name=cc.output)

        self.logger.info("Tracing from %s", start)
        # From start through crossing
        ep1 = pass_crossing(start)
        if not ep1:
            self.logger.info("No OSC crossing from input")
            return
        # Get connected
        ep2 = self.get_peer(ep1)
        if not ep2:
            self.logger.info("Not connected")
            return
        # Get output node
        ep3 = pass_crossing(ep2)
        if not ep3:
            self.logger.info("No OCS crossing to output")
            return
        # Yield path
        yield PathItem(object=start.object, input=start.name, output=ep1.name)
        yield PathItem(object=ep2.object, input=ep2.name, output=ep3.name)

    def sync_ad_hoc_channel(self, ep: Endpoint) -> Tuple[Channel | None, str]:
        """
        Create or update ad-hoc channel.

        Args:
            ep: Starting endpoint

        Returns:
            Channel instance, message
        """

        is_new = False
        path = list(self.iter_path(ep))
        start = Endpoint(object=path[0].object, name=path[0].input)
        end = Endpoint(object=path[1].object, name=path[1].output)
        dbe: list[DBEndpoint] = list(
            DBEndpoint.objects.filter(resource__in=[start.as_resource(), end.as_resource()])
        )
        if not dbe:
            # New channel
            ch = self.create_ad_hoc_channel(discriminator=self.DISCRIMINATOR)
            is_new = True
            # Create endpoints
            dbe = []
            for x in (start, end):
                ep = DBEndpoint(channel=ch, resource=x.as_resource(), is_root=x == start)
                ep.save()
                dbe.append(ep)
        elif len(dbe) == 1:
            # Hanging endpoint
            return None, "Hanging endpoint"
        elif len(dbe) == 2:
            ch = dbe[0].channel
        else:
            return None, "Total trash inside"
        # Update itermediate channels
        # Run provisioning
        jobs = []
        for pi, ep in zip(path, dbe):
            self.logger.info("Getting profile controller for %s", pi.object)
            ctl = ProfileChannelController.get_controller_for_object(pi.object, self.name)
            if not ctl:
                self.logger.info("Controller is not supported, skipping")
                continue
            self.logger.info("Preparing setup")
            job = ctl.setup(ep)
            if job:
                job.name = f"Set up {ep.resource_label}"
                ep.set_last_job(job.id)
                jobs.append(job)
        if jobs:
            job = JobRequest(name="Setup OCS channel", jobs=jobs)
            job.submit()
        # Return
        if is_new:
            return ch, "Channel created"
        return ch, "Channel updated"
