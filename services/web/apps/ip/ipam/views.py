# ---------------------------------------------------------------------
# IP Address space management application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from operator import itemgetter

# Third-party modules modules
import orjson
from noc.core.translation import ugettext as _
from noc.core.ip import IP

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.core.validators import is_ipv4, is_ipv4_prefix, is_ipv6, is_ipv6_prefix
from noc.ip.models.vrf import VRF
from noc.ip.models.prefixbookmark import PrefixBookmark
from noc.ip.models.prefix import Prefix
from noc.main.models.customfield import CustomField
from noc.aaa.models.permission import Permission
from noc.core.colors import get_colors


class IPAMApplication(ExtApplication):
    """
    IPAM application
    """

    title = _("Assigned Addresses")
    menu = [_("Assigned Addresses")]
    extra_permissions = ["bind_vc", "rebase"]
    implied_permissions = {"rebase": ["ip:prefix:rebase"]}

    ADDRESS_SPOT_DIST = 8  # Area around used address to show in free spot
    MAX_IPv4_NET_SIZE = 256  # Cover whole IPv4 prefix with spot if size below

    def get_prefix_spot(self, prefix, sep=True, extra=None):
        """
        Return addresses around existing ones
        """
        extra = extra or []
        p = IP.prefix(prefix.prefix)
        if prefix.afi == "4" and len(p) <= self.MAX_IPv4_NET_SIZE:
            dist = self.MAX_IPv4_NET_SIZE
        else:
            dist = self.ADDRESS_SPOT_DIST
        return p.area_spot(
            [a.address for a in prefix.address_set.all()] + extra, dist=dist, sep=sep
        )

    @view(url=r"^(?P<prefix_id>\d+)/toggle_bookmark/$", method=["GET"], api=True, access="launch")
    def view_toggle_bookmark(self, request, prefix_id):
        """
        Toggle block bookmark status
        """
        prefix = self.get_object_or_404(Prefix, id=int(prefix_id))
        prefix.toggle_bookmark(request.user)
        return {"has_bookmark": prefix.has_bookmark(request.user)}

    @view(
        url=r"get_vrf_prefix/(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>([0-9a-f.:/]+|))/$",
        method=["GET"],
        api=True,
        access="launch",
    )
    def get_vrf_prefix(self, request, vrf_id, afi, prefix):
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))

        if not prefix:
            prefix = VRF.IPv4_ROOT if afi == "4" else VRF.IPv6_ROOT
        if (afi == "4" and (not is_ipv4_prefix(prefix) or not vrf.afi_ipv4)) or (
            afi == "6" and (not is_ipv6_prefix(prefix) or not vrf.afi_ipv6)
        ):
            return self.response_forbidden("Invalid prefix")
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        return self.prefix_contents(request, prefix=prefix)

    @view(url=r"^contents/(?P<prefix_id>\d+)/$", method=["GET"], api=True, access="launch")
    def get_prefix_content(self, request, prefix_id):
        prefix = self.get_object_or_404(Prefix, id=int(prefix_id))
        return self.prefix_contents(request, prefix=prefix)

    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/quickjump/$", url_name="quickjump", access="view")
    def view_quickjump(self, request, vrf_id, afi):
        """
        Quickjump to closest suitable block
        """

        # Interpolate string to valid IPv4 address
        def interpolate_ipv4(s):
            p = s.split(".")
            if len(p) > 4:
                return None
            elif len(p) < 4:
                p += ["0"] * (4 - len(p))
            s = ".".join(p)
            if not is_ipv4(s):
                return None
            return s

        # Interpolate string to valid IPv6 address
        # @todo: implement
        def interpolate_ipv6(s):
            if not is_ipv6(s):
                return None
            return s

        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        if (afi == "4" and not vrf.afi_ipv4) or (afi == "6" and not vrf.afi_ipv6):
            return self.response_forbidden("Invalid AFI")
        if request.body:
            d = orjson.loads(request.body)
            prefix = d["jump"].strip()
            # Interpolate prefix
            if afi == "4":
                prefix = interpolate_ipv4(prefix)
            else:
                prefix = interpolate_ipv6(prefix)
            if not prefix:
                return self.response_bad_request("Invalid address")
            # Find prefix
            prefix = Prefix.get_parent(vrf, afi, prefix)
            return {"id": prefix.id}
        return self.response_redirect_to_referrer(request)

    def prefix_contents(self, request, prefix):
        vrf = prefix.vrf
        # List of nested prefixes
        # @todo: prefetch_related
        prefixes = list(prefix.children_set.select_related().order_by("prefix"))
        # Bulk utilization
        # Prefix.update_prefixes_usage(prefixes)
        # Free prefixes
        free_prefixes = list(IP.prefix(prefix.prefix).iter_free([pp.prefix for pp in prefixes]))
        # Get permissions
        user = request.user
        can_view = prefix.can_view(user)
        can_change = prefix.can_change(user)
        can_bind_vc = can_change and Permission.has_perm(user, "ip:ipam:bind_vc")
        can_change_maintainers = user.is_superuser
        can_add_prefix = can_change
        # can_add_address = can_change and len(prefixes) == 0
        can_add_address = can_change
        # Bookmarks
        has_bookmark = prefix.has_bookmark(user)
        bookmarks = set(
            b.prefix for b in PrefixBookmark.user_bookmarks(user, vrf=vrf, afi=prefix.afi)
        )
        l_prefixes = sorted(
            (
                [(IP.prefix(pp.prefix), pp, pp.prefix in bookmarks) for pp in prefixes]
                + [(pp, None, False) for pp in free_prefixes]
            ),
            key=lambda x: x[0],
        )
        # List of nested addresses
        addresses = list(prefix.address_set.select_related().order_by("address"))
        # Ranges
        ranges = []
        rs = []
        max_slots = 0
        r_spots = []
        allocated_addresses = set()
        if addresses:
            # Assign ranges colors
            ranges = list(prefix.address_ranges)
            for r, c in zip(ranges, get_colors(len(ranges))):
                r.color = c
                # Schedule ranges
            r_changes = {}  # Address -> (set of entering ranges, set of leaving ranges)
            for r in ranges:
                if r.from_address not in r_changes:
                    r_changes[r.from_address] = (set(), set())
                if r.to_address not in r_changes:
                    r_changes[r.to_address] = (set(), set())
                r_changes[r.from_address][0].add(r)
                r_changes[r.to_address][1].add(r)
                # <!>
                n = (IP.prefix(r.to_address) + 1).address
                if n not in r_changes:
                    r_changes[n] = (set(), set())
            r_spots = list(r_changes)
            # Allocate slots
            used_slots = set()
            free_slots = set()
            r_slots = {}  # Range -> slot
            max_slots = 0
            rs = sorted([[IP.prefix(i), d, []] for i, d in r_changes.items()], key=itemgetter(0))
            for address, d, x in rs:
                entering, leaving = d
                for r in entering:
                    if not free_slots:
                        free_slots.add(max_slots)
                        max_slots += 1
                    spt = free_slots.pop()
                    used_slots.add(spt)
                    r_slots[r] = spt
                for r in leaving:
                    spt = r_slots[r]
                    used_slots.remove(spt)
                    free_slots.add(spt)
            # Assign ranges to slots
            slots = [None] * max_slots
            for r in rs:
                address, [entering, leaving], _ = r
                for e in entering:
                    slots[r_slots[e]] = e
                r[2] = slots[:]
                for ll in leaving:
                    slots[r_slots[ll]] = None
            # Assign slots to addresses
            c = [None] * max_slots
            rrs = rs[:]
            cr = rrs.pop(0) if rrs else None
            for a in addresses:
                allocated_addresses.add(str(a.address))
                address = IP.prefix(a.address)
                while cr and address >= cr[0]:
                    c = cr[2]
                    if rrs:
                        cr = rrs.pop(0)
                    else:
                        break
                a.slots = c
        # Address spot
        if can_add_address:
            c = [None] * max_slots
            rrs = rs[:]
            if rrs:
                cr = rrs.pop(0)
            else:
                cr = None
            spot = []
            for a in self.get_prefix_spot(prefix, extra=r_spots):
                if cr and a is not None and a == cr[0]:
                    c = [None if cc is None else cc.id for cc in cr[2]]
                    if rrs:
                        cr = rrs.pop(0)
                spot += [(None if a is None else a.address, c)]
            # spot += [(None if a is None else a.address, c, a in special_addr)]
            # spot = ujson.dumps(spot)
            # spot = JSONEncoder(ensure_ascii=False).encode(spot)
        else:
            spot = None
        can_ping = spot is not None and len([a for a in addresses if a.managed_object]) > 0
        prefix_info = self.get_info_block(prefix.afi, prefix, addresses)
        path = [Prefix.objects.get(id=pp) for pp in prefix.get_path()]
        return {
            "id": prefix.id,
            "name": prefix.prefix,
            "vrf": prefix.vrf.id,
            "vrf__label": f"{prefix.vrf.name} ({prefix.vrf.vpn_id})",
            "description": prefix.description,
            "afi": prefix.afi,
            "profile": prefix.profile.name,
            "state": prefix.state.name,
            "maintainers": [m.username for m in prefix.maintainers],
            "has_bookmark": has_bookmark,
            "permissions": {
                "view": can_view,
                "change": can_change,
                "bind_vc": can_bind_vc,
                "change_maintainers": can_change_maintainers,
                "add_prefix": can_add_prefix,
                "delete_prefix": True,
                "add_address": can_add_address,
                "ping": can_ping,
            },
            "path": [{"id": p.id, "parent_id": p.parent_id, "name": p.prefix} for p in path],
            "prefixes": [
                (
                    {
                        "id": p.id,
                        "name": p.prefix,
                        "row_class": p.profile.style.css_class_name if p.profile.style else "",
                        "has_bookmark": is_bookmarks,
                        "description": p.description,
                        "afi": p.afi,
                        "project": p.project.code if p.project else None,
                        "as": f"AS{p.asn.asn}" if p.asn else None,
                        "vlan": p.vlan.name if p.vlan else None,
                        "tt": p.tt,
                        "usage": p.usage_percent,
                        "address_usage": p.address_usage_percent,
                        "labels": p.labels,
                        "state": p.state.name,
                        "state_desc": p.state.description,
                        "isFree": False,
                    }
                    if p
                    else {"name": ip.prefix, "isFree": True}
                )
                for ip, p, is_bookmarks in l_prefixes
            ],
            "addresses": sorted(
                [
                    {
                        "id": a.id,
                        "name": a.name,
                        "row_class": a.profile.style.css_class_name if a.profile.style else "",
                        "address": a.address,
                        "state": a.state.name,
                        "fqdn": a.fqdn if a.fqdn else None,
                        "mac": a.mac if a.mac else None,
                        "mo_id": a.managed_object.id if a.managed_object else None,
                        "mo_name": a.managed_object.name if a.managed_object else None,
                        "is_router": a.managed_object.is_router if a.managed_object else None,
                        "project": a.project.code if a.project else None,
                        "subinterface": a.subinterface if a.subinterface else None,
                        "short_desc": a.short_description,
                        "desc": a.description,
                        "source": {
                            "M": "Manual",
                            "i": "Interface",
                            "m": "Mgmt",
                            "d": "DHCP",
                            "n": "Neighbor",
                            "P": "Ping",
                        }.get(a.source, "-"),
                        "tt": a.tt,
                        "labels": a.labels,
                        "isFree": False,
                    }
                    for a in addresses
                ]
                + (
                    [
                        {"address": z[0], "isFree": True}
                        for z in spot
                        if str(z[0]) not in allocated_addresses and z[0] is not None
                    ]
                    if spot
                    else []
                ),
                key=lambda x: IP.prefix(x["address"]) if x["address"] else "",
            ),
            "info": dict(prefix_info),
            "ranges": [
                {
                    "name": r.name,
                    "description": r.description,
                    "from_address": r.from_address,
                    "to_address": r.to_address,
                    "color": r.color,
                }
                for r in ranges
            ],
            "bookmarks": [
                {"id": b.id, "text": b.prefix}
                for b in PrefixBookmark.user_bookmarks(user, vrf=vrf, afi=prefix.afi)
            ],
        }

    def get_info_block(self, afi, prefix, addresses):
        # Prepare block info
        prefix_info = [("Network", prefix.prefix)]
        if afi == "4":
            prefix_info += [
                ("Broadcast", prefix.broadcast),
                ("Netmask", prefix.netmask),
                ("Widlcard", prefix.wildcard),
                ("Size", prefix.size),
                ("Usage", prefix.usage_percent),
            ]
        if addresses:
            prefix_info += [("Used addresses", len(addresses))]
            if afi == "4":
                free = prefix.size - len(addresses)
                prefix_info += [("Free addresses", free - 2 if free >= 2 else free)]
        # Prefix discovery
        dmap = {"E": "Enabled", "D": "Disabled"}
        if prefix.prefix_discovery_policy == "P":
            t = "Profile (%s)" % dmap[prefix.profile.prefix_discovery_policy]
        else:
            t = dmap[prefix.prefix_discovery_policy]
        prefix_info += [("Prefix Discovery", t)]
        # Address discovery
        if prefix.address_discovery_policy == "P":
            t = "Profile (%s)" % dmap[prefix.profile.address_discovery_policy]
        else:
            t = dmap[prefix.address_discovery_policy]
        prefix_info += [("Address Discovery", t)]
        # Source
        prefix_info += [
            (
                "Source",
                {"M": "Manual", "i": "Interface", "w": "Whois Route", "n": "Neighbor"}.get(
                    prefix.source, "-"
                ),
            )
        ]
        #
        # Add custom fields
        for f in CustomField.table_fields("ip_prefix"):
            if f.is_hidden:
                continue
            v = getattr(prefix, f.name)
            prefix_info += [(f.label, v if v is not None else "")]
        return prefix_info
