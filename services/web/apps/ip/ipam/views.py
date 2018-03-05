# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IP Address space management application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from operator import itemgetter
# Third-party modules modules
from django import forms
from django.db.models import Q
from django.utils.simplejson.encoder import JSONEncoder
from django.utils.translation import ugettext_lazy as _
from noc.core.ip import IP
# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.lib.validators import is_ipv4, is_ipv4_prefix, is_ipv6, is_ipv6_prefix
from noc.ip.models.address import Address
from noc.ip.models.addressrange import AddressRange
from noc.ip.models.prefix import Prefix
from noc.ip.models.prefixaccess import PrefixAccess
from noc.ip.models.prefixbookmark import PrefixBookmark
from noc.ip.models.vrf import VRF
from noc.ip.models.vrfgroup import VRFGroup
from noc.main.models.customfield import CustomField
from noc.main.models.permission import Permission
from noc.core.colors import get_colors


class IPAMApplication(ExtApplication):
    title = _("Assigned Addresses")
    extra_permissions = ["bind_vc", "rebase"]
    implied_permissions = {
        "rebase": ["ip:prefix:rebase"]
    }

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
        return p.area_spot([a.address for a in prefix.address_set.all()] + extra,
                           dist=dist, sep=sep)

    @view(url=r"^$", url_name="index", menu="Assigned Addresses",
          access="view")
    def view_index(self, request):
        """
        Display VRF list
        @todo: Display only VRFs accessible by user
        """
        # Check only one active VRF with only one active address family exists
        vl = list(VRF.objects.filter(state__is_provisioned=True))
        if len(vl) == 1:
            vrf = vl.pop()
            if vrf.afi_ipv4 ^ vrf.afi_ipv6:
                # Single active VRF with single active AFI, Jump to VRF index
                if vrf.afi_ipv4:
                    afi = "4"
                    root = "0.0.0.0/0"
                else:
                    afi = "6"
                    root = "::/0"
                return self.response_redirect("ip:ipam:vrf_index", vrf.id, afi,
                                              root)
        # Get search query
        query = ""
        if "q" in request.GET:
            query = request.GET["q"]
            q = Q(name__icontains=query) | Q(rd=query) | Q(
                description__icontains=query)
        else:
            q = Q()
        # Display grouped VRFs
        q_afi = Q(afi_ipv4=True) | Q(afi_ipv6=True)
        groups = []
        for vg in VRFGroup.objects.all().order_by("name"):
            vrfs = list(vg.vrf_set.filter(state__is_provisioned=True).filter(q_afi).filter(q).order_by("name"))
            if len(vrfs):
                # Set up bookmarks
                for v in vrfs:
                    v.bookmarks = PrefixBookmark.user_bookmarks(request.user,
                                                                vrf=v)
                    # Add to groups
                groups += [(vg, vrfs)]
        return self.render(request, "index.html", groups=groups, query=query)

    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>[0-9a-f.:/]+)/$",
          url_name="vrf_index", access="view")
    def view_vrf_index(self, request, vrf_id, afi, prefix):
        """
        Display VRF Index
        """
        # Validate
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        if ((afi == "4" and
             (not is_ipv4_prefix(prefix)) or not vrf.afi_ipv4) or
                (afi == "6" and (not is_ipv6_prefix(prefix) or not vrf.afi_ipv6))):
            return self.response_forbidden("Invalid prefix")
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        # Get prefix path
        path = []
        p = prefix.parent
        while p:
            path = [p] + path
            p = p.parent
        # Process description
        short_description = prefix.short_description
        long_description = prefix.description if prefix.description != short_description else None
        # List of nested prefixes
        # @todo: prefetch_related
        prefixes = list(prefix.children_set.select_related().order_by("prefix"))
        # Get permissions
        user = request.user
        can_view = prefix.can_view(user)
        can_change = prefix.can_change(user)
        can_bind_vc = can_change and Permission.has_perm(
            user, "ip:ipam:bind_vc")
        can_change_maintainers = user.is_superuser
        can_add_prefix = can_change
        can_add_address = can_change and len(prefixes) == 0
        # Add free prefixes
        free_prefixes = list(
            IP.prefix(prefix.prefix).iter_free([pp.prefix for pp in prefixes]))
        l_prefixes = sorted(
            ([(True, IP.prefix(pp.prefix), pp) for pp in prefixes] +
             [(False, pp) for pp in free_prefixes]), key=lambda x: x[1])
        # List of nested addresses
        # @todo: prefetch_related
        addresses = list(prefix.address_set.select_related().order_by("address"))
        # Prepare block info
        prefix_info = [
            ("Network", prefix.prefix)
        ]
        if afi == "4":
            prefix_info += [
                ("Broadcast", prefix.broadcast),
                ("Netmask", prefix.netmask),
                ("Widlcard", prefix.wildcard),
                ("Size", prefix.size),
                ("Usage", prefix.usage_percent)
            ]
        if addresses:
            prefix_info += [("Used addresses", len(addresses))]
            if afi == "4":
                free = prefix.size - len(addresses)
                prefix_info += [
                    ("Free addresses", free - 2 if free >= 2 else free)
                ]
        t = {
            "E": "Enabled",
            "D": "Disabled"
        }[prefix.effective_ip_discovery]
        if prefix.enable_ip_discovery == "I":
            t = "Inherit (%s)" % t
        prefix_info += [("IP Discovery", t)]
        #
        ippools = prefix.ippools
        # Add custom fields
        for f in CustomField.table_fields("ip_prefix"):
            v = getattr(prefix, f.name)
            prefix_info += [(f.label, v if v is not None else "")]
        # Bookmarks
        has_bookmark = prefix.has_bookmark(user)
        bookmarks = PrefixBookmark.user_bookmarks(user, vrf=vrf, afi=afi)
        # Ranges
        ranges = []
        rs = []
        max_slots = 0
        r_spots = []
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
            r_spots = r_changes.keys()
            # Allocate slots
            used_slots = set()
            free_slots = set()
            r_slots = {}  # Range -> slot
            max_slots = 0
            rs = sorted([[IP.prefix(i), d, []] for i, d in r_changes.items()],
                        key=itemgetter(0))
            for address, d, x in rs:
                entering, leaving = d
                for r in entering:
                    if not free_slots:
                        free_slots.add(max_slots)
                        max_slots += 1
                    s = free_slots.pop()
                    used_slots.add(s)
                    r_slots[r] = s
                for r in leaving:
                    s = r_slots[r]
                    used_slots.remove(s)
                    free_slots.add(s)
            # Assign ranges to slots
            slots = [None] * max_slots
            for r in rs:
                address, [entering, leaving], _ = r
                for e in entering:
                    slots[r_slots[e]] = e
                r[2] = slots[:]
                for l in leaving:
                    slots[r_slots[l]] = None
            # Assign slots to addresses
            c = [None] * max_slots
            rrs = rs[:]
            cr = rrs.pop(0) if rrs else None
            for a in addresses:
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
            spot = JSONEncoder(ensure_ascii=False).encode(spot)
        else:
            spot = None
        can_ping = spot is not None and len(
            [a for a in addresses if a.managed_object]) > 0
        # Build custom styles
        styles = {}
        if prefix.profile.style:
            styles[prefix.profile.style.css_class_name] = prefix.profile.style.css
        for p in prefixes:
            if p.profile.style and p.profile.style.css_class_name not in styles:
                styles[p.profile.style.css_class_name] = p.profile.style.css
        for a in addresses:
            if a.profile.style and a.profile.style.css_class_name not in styles:
                styles[a.profile.style.css_class_name] = a.profile.style.css
        styles = "\n".join(styles.values())
        # Render
        return self.render(request, "vrf_index.html",
                           vrf=vrf, afi=afi, prefix=prefix, path=path,
                           short_description=short_description,
                           long_description=long_description,
                           prefixes=prefixes, addresses=addresses,
                           ippools=ippools,
                           prefix_info=prefix_info,
                           display_empty_message=not addresses and not prefixes,
                           can_view=can_view, can_change=can_change,
                           can_bind_vc=can_bind_vc,
                           can_change_maintainers=can_change_maintainers,
                           can_add_prefix=can_add_prefix,
                           can_add_address=can_add_address,
                           has_bookmark=has_bookmark, bookmarks=bookmarks,
                           spot=spot, can_ping=can_ping, styles=styles,
                           ranges=ranges, max_slots=max_slots,
                           l_prefixes=l_prefixes)

    class QuickJumpForm(forms.Form):
        jump = forms.CharField()

    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/quickjump/$",
          url_name="quickjump", access="view")
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
        if request.POST:
            form = self.QuickJumpForm(request.POST)
            if form.is_valid():
                prefix = form.cleaned_data["jump"].strip()
                # Interpolate prefix
                if afi == "4":
                    prefix = interpolate_ipv4(prefix)
                else:
                    prefix = interpolate_ipv6(prefix)
                if not prefix:
                    self.message_user(request, _("Invalid address"))
                    return self.response_redirect_to_referrer(request)
                # Find prefix
                prefix = Prefix.get_parent(vrf, afi, prefix).prefix
                # Redirect
                self.message_user(request, _("Redirected to %(prefix)s") % {
                    "prefix": prefix})
                return self.response_redirect("ip:ipam:vrf_index", vrf.id, afi,
                                              prefix)
        return self.response_redirect_to_referrer(request)

    @view(
        url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/toggle_bookmark/$",
        url_name="toggle_bookmark", access="view")
    def view_toggle_bookmark(self, request, vrf_id, afi, prefix):
        """
        Toggle block bookmark status
        """
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        if ((afi == "4" and not vrf.afi_ipv4) or
                (afi == "6" and not vrf.afi_ipv6)):
            return self.response_forbidden("Invalid AFI")
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        user = request.user
        status = prefix.toggle_bookmark(user)
        if status:
            self.message_user(request, _("Bookmark set to %(prefix)s") % {
                "prefix": prefix.prefix})
        else:
            self.message_user(request, _("Bookmark removed from %(prefix)s") % {
                "prefix": prefix.prefix})
        return self.response_redirect_to_referrer(request)

    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/delete/$",
          url_name="delete_prefix", access="change")
    def view_delete_prefix(self, request, vrf_id, afi, prefix):
        """
        Delete prefix
        """
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        if (afi == "4" and not vrf.afi_ipv4) or (afi == "6" and not vrf.afi_ipv6):
            return self.response_forbidden("Invalid AFI")
        if not PrefixAccess.user_can_change(request.user, vrf, afi, prefix):
            return self.response_forbidden()
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        parent = prefix.parent
        if not parent:
            return self.response_forbidden("Cannot delete root prefix")
        if request.POST:
            if "scope" in request.POST and request.POST["scope"][0] in ("p", "r"):
                if "delete_transition" in request.POST:
                    prefix_transition = prefix.ipv6_transition if prefix.ipv6_transition else prefix.ipv4_transition
                    if request.POST["scope"] == "p":
                        # Delete prefix only
                        prefix_transition.delete()
                        self.message_user(request, _(
                            "Prefix %(prefix)s has been successfully deleted") % {
                            "prefix": prefix_transition.prefix})
                    else:
                        # Delete recursive prefixes
                        prefix_transition.delete_recursive()
                        self.message_user(request, _(
                            "Prefix %(prefix)s and all descendans have been successfully deleted") % {
                            "prefix": prefix_transition.prefix})
                if request.POST["scope"] == "p":
                    # Delete prefix only
                    prefix.delete()
                    self.message_user(request, _(
                        "Prefix %(prefix)s has been successfully deleted") % {
                        "prefix": prefix.prefix})
                else:
                    # Delete recursive prefixes
                    prefix.delete_recursive()
                    self.message_user(request, _(
                        "Prefix %(prefix)s and all descendans have been successfully deleted") % {
                        "prefix": prefix.prefix})
                return self.response_redirect("ip:ipam:vrf_index", vrf.id, afi,
                                              parent.prefix)
            # Display form
        return self.render(request, "delete_prefix.html", prefix=prefix)

    @view(
        url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<address>[^/]+)/delete_address/$",
        url_name="delete_address", access="change")
    def view_delete_address(self, request, vrf_id, afi, address):
        """
        Delete address
        """
        # Validate
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        if (afi == "4" and not vrf.afi_ipv4) or (afi == "6" and not vrf.afi_ipv6):
            return self.response_forbidden("Invalid AFI")
        address = self.get_object_or_404(Address, vrf=vrf, afi=afi,
                                         address=address)
        if not PrefixAccess.user_can_change(request.user, vrf, afi,
                                            address.address):
            return self.response_forbidden()
            # Check not in locked range
        if AddressRange.address_is_locked(vrf, afi, address.address):
            self.message_user(request, _(
                "Address %(address)s is in the locked range") % {
                "address": address.address})
            return self.response_redirect(
                "ip:ipam:vrf_index", vrf.id, afi,
                address.prefix.prefix)
        # Delete
        prefix = address.prefix
        address.delete()
        # Redirect
        self.message_user(request, _("Address %(address)s deleted") % {
            "address": address.address})
        return self.response_redirect("ip:ipam:vrf_index", vrf.id, afi,
                                      prefix.prefix)

    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/ping_check/$",
          url_name="ping_check", access="change")
    def view_ping_check(self, request, vrf_id, afi, prefix):
        """
        AJAX handler to run ping_task
        """
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        p = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        # Detect at least one managed objects in block
        r = list(p.address_set.filter(managed_object__isnull=False))
        if not r:
            return self.render_json(None)
        # Get addresses to ping
        # addresses = [a.address for a in self.get_prefix_spot(p, sep=False)]
        # @todo: Call pinger with addresses

    def user_access_list(self, user):
        """
        Row-based access
        """
        def p(a):
            r = []
            if a.can_view:
                r += ["V"]
            if a.can_change:
                r += ["C"]
            return ", ".join(r)

        return ["%s: %s (%s)" % (a.vrf.name, a.prefix, p(a)) for a in
                PrefixAccess.objects.filter(user=user).order_by("vrf__name",
                                                                "prefix")]

    def user_access_change_url(self, user):
        return self.site.reverse("ip:prefixaccess:changelist",
                                 QUERY={"user__id__exact": user.id})
