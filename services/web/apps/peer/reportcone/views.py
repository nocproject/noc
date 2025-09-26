# ---------------------------------------------------------------------
# Peer cone analysys
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.simplereport import SimpleReport, TableColumn
from noc.peer.models.peer import Peer
from noc.peer.models.whoiscache import WhoisCache
from noc.core.ip import IP
from noc.core.translation import ugettext as _


class ReportLOC(SimpleReport):
    title = _("Cone Analysis")

    def get_data(self, request):
        def ppower(prefix):
            m = int(prefix.split("/")[1])
            if m <= powermask:
                return 2 * (powermask - m)
            return 0

        powermask = 24
        r = []  # (Descption, as, filter, cone)
        peers = {}  # peer id -> peer
        cone_powers = {}  # peer id -> power
        uniq_powers = {}  # peer id -> power
        prefixes = {}  # Prefix -> set(peer ids)
        for p in Peer.objects.filter(status="A").exclude(import_filter="ANY"):
            peers[p.id] = p
            cone_powers[p.id] = 0
            for cp in WhoisCache.resolve_as_set_prefixes(p.import_filter, optimize=True):
                # Get powers
                cone_powers[p.id] += ppower(cp)
                # Assign to prefixes
                for i in IP.prefix(cp).iter_cover(powermask):
                    pfx = i.prefix
                    try:
                        prefixes[pfx].add(p.id)
                    except KeyError:
                        prefixes[pfx] = {p.id}
        # Calculate unique powers
        for pfx in prefixes:
            pfx_peers = prefixes[pfx]
            if len(pfx_peers) == 1:
                # Unique
                peer = list(pfx_peers)[0]
                try:
                    uniq_powers[peer] += 1
                except KeyError:
                    uniq_powers[peer] = 1
        # Build result
        for peer_id in peers:
            p = peers[peer_id]
            r += [
                (
                    p.description,
                    "AS%d" % p.remote_asn,
                    p.import_filter,
                    cone_powers.get(peer_id, 0),
                    uniq_powers.get(peer_id, 0),
                )
            ]
        r = sorted(r, key=lambda x: -x[4])
        return self.from_dataset(
            title=self.title,
            columns=[
                "Peer",
                "ASN",
                "Import Filter",
                TableColumn("Cone Power", format="numeric", align="right"),
                TableColumn("Uniq. Cone Power", format="numeric", align="right"),
            ],
            data=r,
        )
