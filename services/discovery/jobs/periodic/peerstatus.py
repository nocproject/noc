# ---------------------------------------------------------------------
# Peer Status check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.peer.models.peer import Peer
from noc.peer.models.peerprofile import PeerProfile
from noc.core.bgp import BGPState


class PeerStatusCheck(DiscoveryCheck):
    """Peer status discovery"""

    name = "peerstatus"
    required_script = "get_bgp_peer_status"

    def handler(self):

        has_bgp_peers = self.has_capability("DB | BGP Peers")
        if not has_bgp_peers:
            self.logger.info("No BGP Peer discovered. Skipping BGP peer status check")
            return
        self.logger.info("Checking BGP Peer statuses")
        peers = {
            p.remote_ip: p
            for p in Peer.objects.filter(
                managed_object=self.object.id,
                profile__in=PeerProfile.get_with_status_discovery(),
            )
        }
        if not peers:
            self.logger.info("No BGP Peers with status discovery enabled. Skipping")
            return
        hints = [{"peer": key} for key in peers] or None
        result = self.object.scripts.get_bgp_peer_status(peers=hints)
        self.logger.info("Result: %s", result)
        now = datetime.datetime.now().replace(microsecond=0)
        for p in result:
            nei = p["neighbor"]
            if nei not in peers:
                self.logger.info("Unknown peer. Skipping")
                continue
            if "status_duration" in p:
                state_changed = now - datetime.timedelta(seconds=p["status_duration"])
            else:
                state_changed = now
            peer = peers[nei]
            ostatus = BGPState(p["status"])
            astatus = p.get("admin_status")
            if peer.oper_status != ostatus.value:
                self.logger.info("[%s] set status to %s (when: %s)", nei, ostatus, state_changed)
                # peer.set_oper_status(ostatus.value, timestamp=state_changed)
            if astatus is False:
                # If admin_down send expired signal
                peer.fire_event("down")
            else:
                peer.fire_event("on")
            if ostatus == BGPState.ESTABLISHED:
                peer.fire_event("seen")
