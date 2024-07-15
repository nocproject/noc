# ----------------------------------------------------------------------
# OTNOTUTracer class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable, List

# NOC modules
from noc.inv.models.object import Object
from noc.core.channel.types import ChannelKind, ChannelTopology
from .base import BaseTracer, Endpoint, PathItem


class OTNOTUTracerTracer(BaseTracer):
    """
    OTN OTU level tracer
    """

    name = "otn_otu"
    kind = ChannelKind.L1
    topology = ChannelTopology.P2P
    tech_domain = "otn_otu"
    adhoc_bidirectional = True

    def iter_endpoints(self, obj: Object) -> Iterable[Endpoint]:
        for c in obj.model.connections:
            if not c.protocols:
                continue
            for pvi in c.protocols:
                if pvi.protocol.code.startswith("OTU") and self.is_connected(obj, c.name):
                    yield Endpoint(object=obj, name=c.name)

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
        path = [PathItem(object=xcvr, input=None, output=out_conn)]
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
