# ----------------------------------------------------------------------
# OTNOSCController class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable, Any

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
    label = "OSC"
    kind = ChannelKind.L1
    topology = ChannelTopology.UP2P
    tech_domain = "otn_osc"
    adhoc_bidirectional = False
    adhoc_endpoints = True
    DISCRIMINATOR = "osc::outband"

    def iter_endpoints(self, obj: Object) -> Iterable[Endpoint]:
        for c in obj.model.connections:
            for pvi in obj.iter_connection_effective_protocols(c.name):
                if pvi.protocol.code == "OSC" and pvi.direction == ">":
                    yield Endpoint(object=obj, name=c.name)
                    break

    def iter_path(self, start: Endpoint) -> Iterable[PathItem]:
        def pass_crossing(ep: Endpoint) -> Endpoint | None:
            for cc in ep.object.iter_cross(ep.name, [self.DISCRIMINATOR]):
                if cc.input_discriminator == self.DISCRIMINATOR:
                    return Endpoint(object=ep.object, name=cc.output)

        self.logger.info("Tracing from %s", start.label)
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

    def sync_ad_hoc_channel(
        self,
        name: str,
        ep: Endpoint,
        channel: Channel | None = None,
        dry_run: bool = False,
        **kwargs: Any,
    ) -> tuple[Channel | None, str]:

        is_new = False
        path = list(self.iter_path(ep))
        start = Endpoint(object=path[0].object, name=path[0].input)
        end = Endpoint(object=path[1].object, name=path[1].output)
        dbe: list[DBEndpoint] = list(
            DBEndpoint.objects.filter(resource__in=[start.as_resource(), end.as_resource()])
        )
        if not dbe:
            # New channel
            channel = self.create_ad_hoc_channel(name=name, discriminator=self.DISCRIMINATOR)
            is_new = True
            # Create endpoints
            dbe = []
            for x in (start, end):
                ep = DBEndpoint(channel=channel, resource=x.as_resource(), is_root=x == start)
                ep.save()
                dbe.append(ep)
        elif len(dbe) == 1:
            # Hanging endpoint
            return None, "Hanging endpoint"
        elif len(dbe) == 2:
            if not channel:
                channel = dbe[0].channel
            elif dbe[0].channel != channel:
                return None, "Belongs to other channel"
            self.update_name(channel, name)
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
            job = ctl.setup(ep, dry_run=dry_run)
            if job:
                job.name = f"Set up {ep.resource_label}"
                job.entity = f"ep:{ep.id}"
                jobs.append(job)
        if jobs:
            job = JobRequest(name="Setup OCS channel", jobs=jobs, entity=f"ch:{channel.id}")
            self.logger.info("Submitting job %s", job.id)
            job.submit()
        # Return
        if is_new:
            return channel, "Channel created"
        return channel, "Channel updated"
