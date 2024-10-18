# ----------------------------------------------------------------------
# OTNOTUController class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable, List, Any, Optional

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
        self.logger.info("Tracing from %s", start.label)
        # Get supported OTU protocols
        protocols = set(self.get_supported_protocols(start))
        self.logger.info("Supported protocols: %s", ", ".join(protocols))
        # Get transceiver
        self.logger.debug("Go down")
        xcvr = self.down(start.object, start.name)
        if not xcvr:
            self.logger.info("No transceiver, stopping")
            return
        # Find TX
        out_conn = "tx"
        if not self.get_connection(xcvr, out_conn):
            self.logger.info("No %s connection, stopping", out_conn)
            return
        # Yield transceiver
        path = [
            PathItem(object=start.object, input=None, output=start.name),
            PathItem(object=xcvr, input="in", output=out_conn),
        ]
        #
        ep = self.get_peer(Endpoint(object=xcvr, name=out_conn))
        if not ep:
            self.logger.info("Transceiver is not connected, stopping")
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
            if not ep:
                self.logger.info("Other side of the channel is not connected, stopping")
                return
        if ep.name == "rx":
            end = self.up(ep.object)
            if not end:
                self.logger.info("%s is not connected, stopping.", ep.label)
                return  # Not connected
            path.append(PathItem(object=ep.object, input=ep.name, output="in"))
            other_protocols = self.get_supported_protocols(end)
            if not other_protocols:
                self.logger.info("Does not support OTU: %s, stopping", end)
                return
            if not (protocols.intersection(other_protocols)):
                self.logger.info(
                    "Protocols mismatch. %s supports only %s. Stopping.",
                    end,
                    ", ".join(other_protocols),
                )
                return
            path.append(PathItem(object=end.object, input=end.name, output=None))
            self.logger.info("Traced. Full path: %s", path)
            yield from path
            return
        self.logger.info("%s is not transceiver and not channel entrypoint. Stopping.", ep.label)
        return

    def sync_ad_hoc_channel(
        self,
        name: str,
        ep: Endpoint,
        channel: Channel | None = None,
        dry_run: bool = False,
        **kwargs: Any,
    ) -> tuple[Channel | None, str]:
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

        def otu_discriminator(start: Endpoint, end: Endpoint) -> Optional[str]:
            """Calculate OTU type"""
            # Get from crossing
            s_otu = get_crossing_otu(start)
            e_otu = get_crossing_otu(end)
            if s_otu and e_otu and s_otu == e_otu:
                return f"otu::{s_otu}"
            if s_otu or e_otu:
                return None  # Mismatched types
            # Get common protocol set
            p1 = set(self.get_supported_protocols(start))
            p2 = set(self.get_supported_protocols(end))
            common = p1.intersection(p2)
            if not common:
                return None  # No common set
            # Get highest available
            r = sorted(common, key=otu_rank, reverse=True)[0]
            return f"otu::{r}"

        def get_crossing_otu(ep: Endpoint) -> Optional[str]:
            """Get OTU from crossing."""
            for cc in ep.object.iter_effective_crossing():
                if cc.output == ep.name and cc.output_discriminator:
                    parts = cc.output_discriminator.split("::")
                    return parts[1].replace("ODU", "OTU")
            return None

        def otu_rank(s: str) -> int:
            """Calculate OTU rank for sorting."""
            if s.startswith("OTUC"):
                return 10 * int(s[4:])
            return int(s[3:4])

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
            # Create channel
            discriminator = otu_discriminator(start, end)
            if not discriminator:
                return None, "Incompatibile OTU types"
            channel = self.create_ad_hoc_channel(name=name, discriminator=discriminator)
            is_new = True
            # Create endpoints
            DBEndpoint(channel=channel, resource=start.as_resource()).save()
            DBEndpoint(channel=channel, resource=end.as_resource()).save()
        elif len(dbe) == 1:
            # Hanging endpoint
            return None, "Hanging endpoint"
        elif len(dbe) == 2:
            if dbe[0].channel.id != dbe[1].channel.id:
                return None, "Start and end already belong to the different channels"
            if not channel:
                channel = dbe[0].channel
            elif dbe[0].channel != channel:
                return None, "Belongs to other channel"
            self.update_name(channel, name)
            # Cleanup intermediate channels
            for ep in DBEndpoint.objects.filter(used_by__channel=channel.id):
                ep.used_by = [i for i in ep.used_by if i.channel.id != channel.id]
                ep.save()
        else:
            return None, "Total trash inside"
        # Find and update intermediate channels
        for e in (start, end):
            for pi in self.iter_path(e):
                if pi.channel:
                    sep = Endpoint(object=pi.object, name=pi.input)
                    eep = Endpoint(object=pi.output_object, name=pi.output)
                    ensure_usage(channel, sep)
                    ensure_usage(channel, eep)
        # Return
        if is_new:
            return channel, "Channel created"
        return channel, "Channel updated"
