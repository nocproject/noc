# ----------------------------------------------------------------------
# OTNODUController class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable, Tuple, Optional, List

# NOC modules
from noc.inv.models.object import Object
from noc.core.channel.types import ChannelKind, ChannelTopology
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import Endpoint as DBEndpoint, UsageItem
from .base import BaseController, Endpoint, PathItem
from .otn_otu import OTNOTUController
from ..profile.channel import ProfileChannelController


class OTNODUController(BaseController):
    """
    OTN OTU level controller
    """

    name = "otn_odu"
    kind = ChannelKind.L2
    topology = ChannelTopology.P2P
    tech_domain = "otn_odu"
    adhoc_endpoints = True

    def iter_endpoints(self, obj: Object) -> Iterable[Endpoint]:
        # Check if card has OTU endpoints
        otu_tr = OTNOTUController()
        otu_endpoints = [e.as_resource() for e in otu_tr.iter_endpoints(obj)]
        if not otu_endpoints:
            return
        # Check if card has OTU trails
        if not DBEndpoint.objects.filter(resource__in=otu_endpoints).first():
            return  # No OTU endpoints
        #
        for c in obj.model.connections:
            if not c.protocols:
                continue
            for pvi in c.protocols:
                # @todo: Check for OTU trails from same card
                if pvi.protocol.code.startswith("ODU") and self.is_connected(obj, c.name):
                    yield Endpoint(object=obj, name=c.name)
                    break

    def get_supported_protocols(self, ep: Endpoint) -> List[str]:
        for c in ep.object.model.connections:
            if c.name != ep.name or not c.protocols:
                continue
            return [pvi.protocol.code for pvi in c.protocols if pvi.protocol.code.startswith("ODU")]
        return []

    def iter_path(self, start: Endpoint) -> Iterable[PathItem]:
        self.logger.info("Tracing from %s", start)
        r = []
        # Starting cart
        # Check if we have transceiver
        if not self.is_connected(start.object, start.name):
            self.logger.info("Starting transceiver is not connected")
            return
        # Get supported protocols
        start_protocols = set(self.get_supported_protocols(start))
        if not start_protocols:
            self.logger.info("Starting port does not supports ODU")
            return
        # Get existing exiting protocol and discriminator
        otu_port = None
        discriminator = None
        for cc in start.object.iter_cross(start.name):
            if cc.output_discriminator:
                otu_port = cc.output
                discriminator = cc.output_discriminator
                break
        else:
            self.logger.info("Ingress client port has no ODU crossing")
            return
        # Find OTU channel
        otu_start = Endpoint(object=start.object, name=otu_port)
        otu_eps = DBEndpoint.objects.filter(resource=otu_start.as_resource()).first()
        if not otu_eps:
            self.logger.info("No outgoing OTU")
            return
        r.append(
            PathItem(
                object=start.object,
                input=start.name,
                output=otu_port,
                channel=otu_eps.channel,
                input_discriminator=discriminator,
            )
        )
        # Pass through the OTU channel
        otu_end = self.pass_channel(otu_start)
        if not otu_end:
            self.logger.info("Hanging OTU")
            return
        # Find ending client port
        for cc in otu_end.object.iter_effective_crossing():
            if cc.output == otu_end.name and cc.output_discriminator == discriminator:
                end = Endpoint(object=otu_end.object, name=cc.input)
                break
        else:
            self.logger.info("Egress client port has no ODU crossing")
            return
        # Check protocols
        end_protocols = set(self.get_supported_protocols(end))
        if not end_protocols:
            self.logger.info("End does not support ODU")
            return
        matched_protocols = start_protocols.intersection(end_protocols)
        if not matched_protocols:
            self.logger.info("ODU protocols mismatch")
            return
        if not self.is_connected(end.object, end.name):
            self.logger.info("Missing tranceiver on the end")
            return
        r.append(
            PathItem(
                object=otu_end.object,
                input=otu_end.name,
                output=end.name,
                channel=otu_eps.channel,
                input_discriminator=discriminator,
            )
        )
        yield from r

    def sync_ad_hoc_channel(self, ep: Endpoint) -> Tuple[Optional[Channel], str]:
        """
        Create or update ad-hoc channel.

        Args:
            ep: Starting endpoint

        Returns:
            Channel instance, message
        """

        def ensure_usage(ch: Channel, ep: Endpoint) -> str:
            e = DBEndpoint.objects.filter(resource=ep.as_resource()).first()
            if not e:
                return
            e.used_by += [UsageItem(channel=ch, discriminator=discriminator)]
            e.save()

        def get_channel_odu(s: str) -> str:
            """
            Get channel discriminator from crossing
            """
            last = s.split("::")[-1]
            if "-" in s:
                last, _ = last.split("-", 1)
            return f"odu::{last}"

        is_new = False
        path = list(self.iter_path(ep))
        start = Endpoint(object=path[0].object, name=path[0].input)
        end = Endpoint(object=path[1].object, name=path[1].output)
        discriminator = path[0].input_discriminator
        dbe: list[DBEndpoint] = list(
            DBEndpoint.objects.filter(resource__in=[start.as_resource(), end.as_resource()])
        )
        if not dbe:
            # New channel
            ch = self.create_ad_hoc_channel(discriminator=get_channel_odu(discriminator))
            is_new = True
            # Create endpoints
            dbe = []
            for x in (start, end):
                ep = DBEndpoint(channel=ch, resource=x.as_resource())
                ep.save()
                dbe.append(ep)
        elif len(dbe) == 1:
            # Hanging endpoint
            return None, "Hanging endpoint"
        elif len(dbe) == 2:
            if dbe[0].channel.id != dbe[1].channel.id:
                return None, "Start and end already belong to the different channels"
            ch = dbe[0].channel
            # Cleanup intermediate channels
            for ep in DBEndpoint.objects.filter(used_by__channel=ch.id):
                ep.used_by = [i for i in ep.used_by if i.channel.id != ch.id]
                ep.save()
        else:
            return None, "Total trash inside"
        # Update itermediate channels
        otu_start = Endpoint(object=path[0].object, name=path[0].output)
        otu_end = Endpoint(object=path[1].object, name=path[1].input)
        ensure_usage(ch, otu_start)
        ensure_usage(ch, otu_end)
        # Run provisioning
        for pi, ep in zip(path, dbe):
            self.logger.info("Getting profile controller for %s", pi.object)
            ctl = ProfileChannelController.get_controller_for_object(pi.object, self.name)
            if not ctl:
                self.logger.info("Controller is not supported, skipping")
            self.logger.info("Preparing setup")
            job = ctl.setup(ep)
            if job:
                ep.set_last_job(job.id)
                job.submit()
        # Return
        if is_new:
            return ch, "Channel created"
        return ch, "Channel updated"
