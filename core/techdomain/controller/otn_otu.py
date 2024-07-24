# ----------------------------------------------------------------------
# OTNOTUController class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable, List, Tuple, Optional

# NOC modules
from noc.inv.models.object import Object
from noc.core.channel.types import ChannelKind, ChannelTopology
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import Endpoint as DBEndpoint, UsageItem
from .base import BaseController, Endpoint, PathItem


class OTNOTUController(BaseController):
    """
    OTN OTU level controller
    """

    name = "otn_otu"
    kind = ChannelKind.L1
    topology = ChannelTopology.P2P
    tech_domain = "otn_otu"
    adhoc_bidirectional = True
    adhoc_endpoints = True

    def iter_endpoints(self, obj: Object) -> Iterable[Endpoint]:
        for c in obj.model.connections:
            if not c.protocols:
                continue
            for pvi in c.protocols:
                if pvi.protocol.code.startswith("OTU") and self.is_connected(obj, c.name):
                    yield Endpoint(object=obj, name=c.name)
                    break

    def get_supported_protocols(self, ep: Endpoint) -> List[str]:
        for c in ep.object.model.connections:
            if c.name != ep.name or not c.protocols:
                continue
            return [pvi.protocol.code for pvi in c.protocols if pvi.protocol.code.startswith("OTU")]
        return []

    def iter_path(self, start: Endpoint) -> Iterable[PathItem]:
        self.logger.info("Tracing from %s", start)
        # Get supported OTU protocols
        protocols = set(self.get_supported_protocols(start))
        self.logger.info("Supported protocols: %s", ", ".join(protocols))
        # Get transceiver
        self.logger.debug("Go down")
        xcvr = self.down(start.object, start.name)
        if not xcvr:
            self.logger.info("No transceiver, stoppinng.")
            return
        # Find TX
        out_conn = "tx"
        if not self.get_connection(xcvr, out_conn):
            self.logger.info("No %s connection", out_conn)
            return
        # Yield transceiver
        path = [
            PathItem(object=start.object, input=None, output=start.name),
            PathItem(object=xcvr, input="in", output=out_conn),
        ]
        #
        ep = self.get_peer(Endpoint(object=xcvr, name=out_conn))
        if not ep:
            self.logger.info("Transceiver is not connected")
            return
        # Here we have either another transceiver or channel
        nep = self.pass_channel(ep)
        if nep:
            # Channel
            self.logger.info("Passing through channel %s to %s", nep.channel.name, nep)
            path.append(
                PathItem(
                    object=ep.object,
                    input=ep.name,
                    output_object=nep.object,
                    output=nep.name,
                    channel=nep.channel,
                )
            )
            # Pass to next
            ep = self.get_peer(nep)
        if ep.name == "rx":
            end = self.up(ep.object)
            if not end:
                self.logger.info("%s is not connected", end)
                return  # Not connected
            path.append(PathItem(object=ep.object, input=ep.name, output="in"))
            other_protocols = self.get_supported_protocols(end)
            if not other_protocols:
                self.logger.info("Does not support OTU: %s", end)
                return
            if not (protocols.intersection(other_protocols)):
                self.logger.info(
                    "Protocols mismatch. %s supports only %s", end, ", ".join(other_protocols)
                )
                return
            path.append(PathItem(object=end.object, input=end.name, output=None))
            self.logger.info("Full path: %s", path)
            yield from path
            return
        self.logger.info("%s is not transceiver and not channel entrypoint", ep)
        return

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
            e.used_by += [UsageItem(channel=ch)]
            e.save()

        # Trace path forward
        end = self.trace_path(ep)
        if not end:
            return None, "No forward path"
        # Trace path back
        start = self.trace_path(end)
        if not start:
            return None, "No backward path"
        if start.as_resource() != ep.as_resource():
            return None, "Forward and reverse path mismatch"
        # Check if we have channnel
        is_new = False
        dbe = list(DBEndpoint.objects.filter(resource__in=[start.as_resource(), end.as_resource()]))
        if not dbe:
            # New channel
            # @todo: ADM200 only
            ch = self.create_ad_hoc_channel(discriminator="otu::OTUC2")
            is_new = True
            # Create endpoints
            DBEndpoint(channel=ch, resource=start.as_resource()).save()
            DBEndpoint(channel=ch, resource=end.as_resource()).save()
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
        # Find and update intermediate channels
        for e in (start, end):
            for pi in self.iter_path(e):
                if pi.channel:
                    sep = Endpoint(object=pi.object, name=pi.input)
                    eep = Endpoint(object=pi.output_object, name=pi.output)
                    ensure_usage(ch, sep)
                    ensure_usage(ch, eep)
        # Return
        if is_new:
            return ch, "Channel created"
        return ch, "Channel updated"
