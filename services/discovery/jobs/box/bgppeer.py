# ---------------------------------------------------------------------
# BGPPeer check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from collections import defaultdict
from pydantic import BaseModel
from typing import Dict, List, Tuple, Any, Optional

# NOC modules
from noc.services.discovery.jobs.base import PolicyDiscoveryCheck
from noc.core.ip import IP
from noc.core.perf import metrics
from noc.sa.interfaces.igetbgppeer import IGetBGPPeer
from noc.peer.models.asn import AS
from noc.peer.models.peer import Peer


class DiscoveredPeer(BaseModel):
    remote_address: Any
    local_as: int
    remote_as: Optional[int] = None
    router_id: Optional[Any] = None
    local_address: Optional[Any] = None
    protocol: str = "bgp"
    type: str = "external"
    admin_status: bool = True
    description: Optional[str] = None
    import_filter_name: Optional[str] = None
    export_filter_name: Optional[str] = None


class BGPPeerCheck(PolicyDiscoveryCheck):
    """
    BGP Peer discovery
    """

    name = "bgppeer"

    BGP_PEER_QUERY = """(
      Match("virtual-router", vr, "forwarding-instance", instance, "protocols", "bgp", "neighbors", peer) or
      Match("virtual-router", vr, "forwarding-instance", instance, "protocols", "bgp", "neighbors", peer, "description", description) or
      Match("virtual-router", vr, "forwarding-instance", instance, "protocols", "bgp", "neighbors", peer, "type", type) or
      Match("virtual-router", vr, "forwarding-instance", instance, "protocols", "bgp", "neighbors", peer, "admin-status", admin_status) or
      Match("virtual-router", vr, "forwarding-instance", instance, "protocols", "bgp", "neighbors", peer, "remote-as", remote_as) or
      Match("virtual-router", vr, "forwarding-instance", instance, "protocols", "bgp", "neighbors", peer, "local-as", local_as) or
      Match("virtual-router", vr, "forwarding-instance", instance, "protocols", "bgp", "neighbors", peer, "local-address", local_address) or
      Match("virtual-router", vr, "forwarding-instance", instance, "protocols", "bgp", "neighbors", peer, "router-id", router_id) or
      Match("virtual-router", vr, "forwarding-instance", instance, "protocols", "bgp", "neighbors", peer, "import-filter", import_filter_name) or
      Match("virtual-router", vr, "forwarding-instance", instance, "protocols", "bgp", "neighbors", peer, "export-filter", export_filter_name)
    ) and Group("vr", "instance", "peer")"""

    def handler(self):
        peers = self.get_bgp_peer()
        if peers is None:
            return
        self.sync_peers(peers)
        self.update_caps({"DB | BGP Peers": len(peers)}, source="bgppeer")

    def get_bgp_peer(self) -> Dict[Tuple[AS, IP], DiscoveredPeer]:
        """Return BGP Peer. Local AS, RemoteIP"""
        r = {}
        data = self.get_data() or []
        for d in data:
            for p in d["peers"]:
                p = DiscoveredPeer.model_validate(p)
                local_as = self.ensure_asn(p.local_as)
                if not local_as:
                    self.logger.warning("[AS%s] Not found AS. Skipping...", p.local_as)
                    continue
                elif not local_as.profile.enable_discovery_peer:
                    self.logger.info("[AS%s] Disabled Peer discovery for AS.", p.local_as)
                    continue
                r[(local_as, p.remote_address)] = p
        return r

    def sync_peers(self, peers: Dict[Tuple[AS, IP], DiscoveredPeer]):
        """
        Apply Peers to database
        Attrs:
            peers: Discovered Peers
        """
        # VRF Processed
        for las, remote_ip in peers:
            self.logger.debug(
                "[%s|%s] Processed peer data: %s", las, remote_ip, peers[las, remote_ip]
            )
            p = Peer.objects.filter(local_asn=las, remote_ip=remote_ip).first()
            if p:
                self.apply_bgp_peer_changes(p, peers[las, remote_ip])
            else:
                self.create_bgp_peer(las, peers[las, remote_ip])

    def apply_bgp_peer_changes(self, peer: Peer, discovered_peer: DiscoveredPeer):
        """Apply BGP Peer changes and send signals"""
        changes = []
        if peer.remote_asn != discovered_peer.remote_as:
            changes += [f"remote_asn: {peer.remote_asn} -> {discovered_peer.remote_as}"]
            peer.remote_asn = discovered_peer.remote_as
        if peer.local_ip != discovered_peer.local_address:
            changes += [f"local_address: {peer.local_ip} -> {discovered_peer.local_address}"]
            peer.local_ip = discovered_peer.local_address
        if peer.description != discovered_peer.description:
            changes += [f"description: {peer.description} -> {discovered_peer.description}"]
        if peer.managed_object != self.object:
            peer.managed_object = self.object
            changes += [f"managed_object: {peer.managed_object} -> {self.object}"]
        if changes:
            self.logger.info(
                "Changing %s (AS%s): %s",
                peer.remote_ip,
                peer.local_asn,
                ", ".join(changes),
            )
            peer.save()
            metrics["prefix_updated"] += 1
        if discovered_peer.admin_status:
            peer.fire_event("up")
        else:
            peer.fire_event("down")
        peer.fire_event("seen")

    def create_bgp_peer(self, local_as: AS, peer: DiscoveredPeer):
        """Create Peer on Database"""
        now = datetime.datetime.now().replace(microsecond=0)
        p = Peer(
            local_asn=local_as,
            local_ip=peer.local_address,
            remote_asn=peer.remote_as,
            remote_ip=peer.remote_address,
            import_filter=peer.import_filter_name or "default",
            export_filter=peer.export_filter_name or "default",
            description=peer.description,
            first_discovered=now,
            managed_object=self.object,
        )
        self.logger.info(
            "Creating BGP Peer %s (AS%s): remote_as=%s profile=%s",
            p.remote_ip,
            p.local_asn,
            p.remote_asn,
            p.profile.name,
        )
        p.save()
        p.fire_event("seen")
        metrics["bgppeer_created"] += 1

    def ensure_asn(self, asn: int) -> AS:
        """Find AS Number on database and Create if not exists"""
        a = AS.objects.filter(asn=asn).first()
        if a:
            return a
        self.logger.info("[AS%s] Not found AS. Creating...", asn)
        a = AS(asn=asn)
        a.save()
        return a

    # def get_peering_point(self) -> Optional[PeeringPoint]:
    #     """Getting PeeringPoint if configured"""
    #     point = PeeringPoint.objects.filter(local_as=asn).first()
    #     if point:
    #         return point
    #     return None

    # def resolve_local_address(self, address: IP) -> Optional[IP]:
    #     """Resolve Local Address by IPAM"""
    #     maybe_addr = [
    #         re.compile((address + 1).address),
    #         re.compile((address - 1).address),
    #     ]
    #     si = SubInterface.objects.filter(
    #         managed_object=self.object, ipv4_addresses__in=maybe_addr
    #     ).first()
    #     if not si and peer.router_id:
    #         return peer.router_id.address
    #     elif not si:
    #         return
    #     return IP.prefix(si.ipv4_addresses[0]).address

    def get_policy(self) -> str:
        return self.object.object_profile.bgpeer_discovery_policy

    def get_data_from_script(self):
        """Not implemented for BGP Discovery"""

    def get_data_from_confdb(self) -> Optional[List[Dict[str, Any]]]:
        """Getting peer from database"""
        r = defaultdict(list)
        for peer in self.confdb.query(self.BGP_PEER_QUERY):
            if peer.get("type", "internal") == "internal" and not peer.get("peer"):
                self.logger.info("[%s] Internal Peer without AS", peer["remote_address"])
                continue
            if "local_address" in peer:
                peer["local_address"] = peer["local_address"].address
            peer["remote_address"] = peer["peer"].address
            del peer["peer"]
            vr = peer.pop("vr", "default")
            peer.pop("router_id", None)
            r[vr].append(peer)
        try:
            return IGetBGPPeer().clean_result(
                [{"virtual_router": k, "peers": v} for k, v in r.items()]
            )
        except ValueError as e:
            self.logger.error("Error getting data by ConfDB query: %s", str(e))
            # Set problem!
            return None
