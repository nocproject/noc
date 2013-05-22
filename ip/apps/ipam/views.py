# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IP Address space management application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
from __future__ import with_statement
from operator import attrgetter, itemgetter
# Django modules
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django import forms
from django.utils.simplejson.encoder import JSONEncoder
# NOC modules
from noc.lib.app import Application, view
from noc.lib.validators import *
from noc.lib.ip import *
from noc.lib.forms import NOCForm
from noc.lib.widgets import *
from noc.lib.colors import *
from noc.sa.interfaces import MACAddressParameter, InterfaceTypeError
from noc.ip.models import *
from noc.main.models import Permission, Style, CustomField, ResourceState
from noc.project.models.project import Project
from noc.peer.models import AS
from noc.vc.models import VCBindFilter
from noc.sa.models import ReduceTask, ManagedObject
from noc.lib.db import SQL


class IPAMAppplication(Application):
    title = "Assigned Addresses"
    extra_permissions = ["bind_vc"]

    ADDRESS_SPOT_DIST = 8    # Area around used address to show in free spot
    MAX_IPv4_NET_SIZE = 256  # Cover whole IPv4 prefix with spot if size below
    ##
    ## Helper functions
    ##
    rx_ipv4_prefix_rest = re.compile(r"(\.0)+/\d+$")
    rx_ipv6_prefix_rest = re.compile(r"(:0+)*/\d+$")

    def get_common_prefix_part(self, afi, p):
        p = IP.prefix(p.prefix)
        if afi == "4":
            if p.mask < 8:
                return ""
            # Align to 8-bit border
            p.mask = (p.mask // 8) * 8
            p = self.rx_ipv4_prefix_rest.sub("", p.normalized.prefix) + "."
        else:
            if p.mask < 16:
                return ""
            # Align to 16-bit border
            p.mask = (p.mask // 16) * 16
            p = self.rx_ipv6_prefix_rest.sub("", p.normalized.prefix)
        return p

    def get_prefix_spot(self, prefix, sep=True, extra=[]):
        """
        Return addresses around existing ones
        """
        p = IP.prefix(prefix.prefix)
        if prefix.afi == "4" and len(p) <= self.MAX_IPv4_NET_SIZE:
            dist = self.MAX_IPv4_NET_SIZE
        else:
            dist = self.ADDRESS_SPOT_DIST
        print "area_spot", [a.address for a in prefix.address_set.all()] + extra, dist, sep
        return p.area_spot([a.address for a in prefix.address_set.all()] + extra,
                           dist=dist, sep=sep)

    def ds_afi(self, afi):
        """
        Return dual-stack pair AFI
        :param afi: "4" or "6"
        :return:
        """
        return "6" if afi == "4" else "4"

    def process_dual_stacking(self, prefix, ds_prefix):
        """
        Process dual-stacking linking
        :param prefix:
        :type prefix: Prefix
        :param ds_prefix:
        :type prefix: str
        """
        if not ds_prefix:
            prefix.clear_transition()
            return

        ds_afi = self.ds_afi(prefix.afi)
        try:
            ds_p = Prefix.objects.get(vrf=prefix.vrf,
                                      afi=ds_afi,
                                      prefix=ds_prefix)
        except Prefix.DoesNotExist:
            # Create paired prefix
            ds_p = Prefix(
                vrf=prefix.vrf,
                afi=ds_afi,
                prefix=ds_prefix,
                asn=prefix.asn,
                description=prefix.description,
                state=prefix.state,
                vc=prefix.vc,
                tags=prefix.tags
            )
            ds_p.save()
        if prefix.afi == "4":
            prefix.ipv6_transition = ds_p
            prefix.save()
        else:
            ds_p.ipv6_transition = prefix
            ds_p.save()

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
        # Display groupped VRFs
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
        can_rebase = can_change and Permission.has_perm(user, "ip:ipam:rebase")
        can_bind_vc = can_change and Permission.has_perm(
            user, "ip:ipam:bind_vc")
        can_change_maintainers = user.is_superuser
        can_add_prefix = can_change
        can_add_address = can_change and len(prefixes) == 0
        # Add free prefixes
        free_prefixes = list(
            IP.prefix(prefix.prefix).iter_free([p.prefix for p in prefixes]))
        l_prefixes = sorted(
            ([(True, IP.prefix(p.prefix), p) for p in prefixes] +
             [(False, p) for p in free_prefixes]), key=lambda x: x[1])
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
            ]
        if addresses:
            prefix_info += [("Used addresses", len(addresses))]
            if afi == "4":
                free = prefix.size - len(addresses)
                prefix_info += [
                    ("Free addresses", free - 2 if free >= 2 else free)
                ]
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
                #<!>
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
            for address, d, _ in rs:
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
                    c = [None if c is None else c.id for c in cr[2]]
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
        if prefix.style:
            styles[prefix.style.css_class_name] = prefix.style.css
        for p in prefixes:
            if p.style and p.style.css_class_name not in styles:
                styles[p.style.css_class_name] = p.style.css
        for a in addresses:
            if a.style and a.style.css_class_name not in styles:
                styles[a.style.css_class_name] = a.style.css
        styles = "\n".join(styles.values())
        # Render
        return self.render(request, "vrf_index.html",
                           vrf=vrf, afi=afi, prefix=prefix, path=path,
                           short_description=short_description,
                           long_description=long_description,
                           prefixes=prefixes, addresses=addresses,
                           prefix_info=prefix_info,
                           display_empty_message=not addresses and not prefixes,
                           can_view=can_view, can_change=can_change,
                           can_rebase=can_rebase,
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
                p = p + ["0"] * (4 - len(p))
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
        if (afi == "4" and not vrf.afi_ipv4) or (
        afi == "6" and not vrf.afi_ipv6):
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

    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/add_prefix/$",
          url_name="add_prefix", access="change")
    def view_add_prefix(self, request, vrf_id, afi, prefix):
        """
        Add prefix
        """
        def get_form_class():
            class AddPrefixForm(NOCForm):
                prefix = forms.CharField(label=_("Prefix"),
                                         help_text=_("IPv%(afi)s prefix") % {
                                             "afi": afi})
                state = forms.ModelChoiceField(label=_("State"),
                    queryset=ResourceState.objects.filter(is_starting=True,
                        is_active=True).order_by("name"),
                    help_text=_("Prefix state")
                )
                project = forms.ModelChoiceField(label=_("Project"),
                    queryset=Project.objects.order_by("code"),
                    help_text=_("Project"),
                    required=False
                )
                asn = forms.ModelChoiceField(
                    label=_("ASN"),
                    queryset=AS.objects.order_by("asn"),
                    help_text=_("AS Number"))
                description = forms.CharField(
                    label=_("Description"),
                    widget=forms.Textarea,
                    required=False)
                tags = forms.CharField(
                    label=_("Tags"),
                    widget=AutoCompleteTags,
                    required=False)
                tt = forms.IntegerField(
                    label=_("TT #"),
                    required=False,
                    help_text=_("Ticket #"))
                style = forms.ModelChoiceField(
                    label=_("Style"),
                    queryset=Style.objects.filter(is_active=True).order_by("name"),
                    required=False,
                    help_text=_("Visual appearance"))
                dual_stack_prefix = forms.CharField(
                    label=_("Dual-stack prefix"),
                    required=False,
                    help_text=_("Appropriative dual-stack allocation")
                )

                def clean_prefix(self):
                    prefix = self.cleaned_data["prefix"]
                    # Validate prefix
                    if afi == "4":
                        check_ipv4_prefix(prefix)
                    else:
                        check_ipv6_prefix(prefix)
                    # Check permissions
                    if not PrefixAccess.user_can_change(request.user, vrf, afi,
                                                        prefix):
                        raise ValidationError(_("Permission denied"))
                    # Check prefix not exists
                    p = Prefix.objects.filter(
                        vrf=vrf, afi=afi, prefix=prefix)
                    if (not p and
                        vrf.vrf_group.address_constraint == "G"):
                        # Prefixes are unique per VRF Group
                        p = Prefix.objects.filter(
                            vrf__in=vrf.vrf_group.vrf_set.exclude(id=vrf.id),
                            afi=afi
                        ).filter(
                            SQL("prefix >>= '%s'" % prefix) |
                            SQL("prefix <<= '%s'" % prefix)
                        ).exclude(parent__isnull=True)
                    if p:
                        raise ValidationError(_("Prefix %s is already exists in vrf %s") % (p[0].prefix, p[0].vrf))
                    return prefix

                def clean_dual_stack_prefix(self):
                    ds_prefix = self.cleaned_data["dual_stack_prefix"]
                    ds_afi = "6" if afi == "4" else "4"
                    if ds_prefix:
                        if afi == "4":
                            check_ipv6_prefix(ds_prefix)
                        else:
                            check_ipv4_prefix(ds_prefix)
                        # Check permissions
                        if not PrefixAccess.user_can_change(request.user, vrf,
                                                            ds_afi, ds_prefix):
                            raise ValidationError(_("Permission denied. "
                                        "Cannot set dual-stack allocation"))
                    return ds_prefix

            # Add custom fields
            self.customize_form(AddPrefixForm, "ip_prefix")
            return AddPrefixForm

        # Validation
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        if ((afi == "4" and not vrf.afi_ipv4) or
            (afi == "6" and not vrf.afi_ipv6)):
            return self.response_forbidden("Invalid AFI")
        parent = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        # Process input
        form_class = get_form_class()
        if request.POST:
            form = form_class(request.POST)
            if form.is_valid():
                # Create prefix
                p = Prefix(vrf=vrf, afi=afi,
                           prefix=form.cleaned_data["prefix"].strip(),
                           state=form.cleaned_data["state"],
                           project=form.cleaned_data["project"],
                           asn=form.cleaned_data["asn"],
                           description=form.cleaned_data["description"],
                           tags=form.cleaned_data["tags"],
                           tt=form.cleaned_data["tt"],
                           style=form.cleaned_data["style"])
                self.apply_custom_fields(
                    p, form.cleaned_data, "ip_prefix")
                with self.form_errors(form):
                    p.save()
                if not form._errors:
                    self.message_user(
                        request,
                        _("Prefix %(prefix)s has been created") % {
                            "prefix": p.prefix})
                    # Process dual-stack linking
                    ds_prefix = form.cleaned_data["dual_stack_prefix"]
                    self.process_dual_stacking(p, ds_prefix)
                    # Redirect depending on submit button pressed
                    if "_continue" in request.POST:
                        return self.response_redirect(
                            "ip:ipam:change_prefix",
                            vrf.id, afi, p.prefix)
                    if "_addanother" in request.POST:
                        return self.response_redirect(
                            "ip:ipam:add_prefix",
                            vrf.id, afi, p.parent.prefix)
                    return self.response_redirect(
                        "ip:ipam:vrf_index",
                        vrf.id, afi, p.prefix)
        else:
            initial = {
                "asn": parent.asn.id,
                "state": ResourceState.get_default()
            }
            if request.GET and "prefix" in request.GET:
                # Prefix set via querystring
                initial["prefix"] = request.GET["prefix"]
            else:
                # Display beginning of prefix
                initial = {
                    "prefix": self.get_common_prefix_part(afi, parent),
                    "state": ResourceState.get_default(),
                    "asn": parent.asn.id
                }
            form = form_class(initial=initial)
            # Suggest blocks of different sizes
        suggestions = []
        if parent:
            p_mask = int(parent.prefix.split("/")[1])
            free = sorted(IP.prefix(parent.prefix).iter_free(
                [p.prefix for p in parent.children_set.all()]),
                          key=attrgetter("mask"))
            if free:
                free.reverse()
                # Find smallest free block possible
                for mask in range(30 if afi == "4" else 64,
                                  max(p_mask + 1, free[-1].mask) - 1, -1):
                    # Find smallest free block possible
                    for p in free:
                        if p.mask <= mask:
                            suggestions += [("%s/%d" % (p.address, mask), 2 ** (
                            32 - mask) if afi == "4" else None)]
                            break
        return self.render(request, "add_prefix.html", vrf=vrf, afi=afi,
                           form=form, suggestions=suggestions)

    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/change/$",
          url_name="change_prefix", access="change")
    def view_change_prefix(self, request, vrf_id, afi, prefix):
        """
        Change prefix
        """
        def get_form_class():
            class EditPrefixForm(NOCForm):
                asn = forms.ModelChoiceField(label=_("ASN"),
                                             queryset=AS.objects.order_by("asn"),
                                             help_text=_("AS Number"))
                state = forms.ModelChoiceField(label=_("State"),
                    queryset=ResourceState.objects.filter(is_active=True).order_by("name"),
                    help_text=_("Prefix state")
                )
                project = forms.ModelChoiceField(label=_("Project"),
                    queryset=Project.objects.order_by("code"),
                    help_text=_("Project"),
                    required=False
                )
                if can_bind_vc:
                    vc = forms.ModelChoiceField(
                        label=_("VC"),
                        queryset=VCBindFilter.get_vcs(
                            vrf, afi, prefix),
                        required=False,
                        help_text=_("VC Related with prefix. Adjust VC Bind Filters if you cannot see required VC"))
                description = forms.CharField(
                    label=_("Description"),
                    widget=forms.Textarea,
                    required=False)
                tags = forms.CharField(
                    label=_("Tags"),
                    widget=AutoCompleteTags,
                    required=False)
                tt = forms.IntegerField(
                    label=_("TT #"),
                    required=False,
                    help_text=_("Ticket #"))
                style = forms.ModelChoiceField(
                    label=_("Style"),
                    queryset=Style.objects.filter(is_active=True).order_by("name"),
                    required=False,
                    help_text=_("Visual appearance"))
                dual_stack_prefix = forms.CharField(
                    label=_("Dual-stack prefix"),
                    required=False,
                    help_text=_("Appropriative dual-stack allocation")
                )

                def clean_dual_stack_prefix(self):
                    ds_prefix = self.cleaned_data["dual_stack_prefix"]
                    ds_afi = "6" if afi == "4" else "4"
                    if ds_prefix:
                        if afi == "4":
                            check_ipv6_prefix(ds_prefix)
                        else:
                            check_ipv4_prefix(ds_prefix)
                        # Check permissions
                        if not PrefixAccess.user_can_change(
                            request.user, vrf, ds_afi, ds_prefix):
                            raise ValidationError(_("Permission denied. "
                                        "Cannot set dual-stack allocation"))
                    return ds_prefix

            self.customize_form(EditPrefixForm, "ip_prefix")
            return EditPrefixForm

        # Validate
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        if ((afi == "4" and not vrf.afi_ipv4) or
            (afi == "6" and not vrf.afi_ipv6)):
            return self.response_forbidden("Invalid AFI")
        if not PrefixAccess.user_can_change(request.user, vrf, afi, prefix):
            return self.response_forbidden()
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        can_bind_vc = Permission.has_perm(request.user, "ip:ipam:bind_vc")
        form_class = get_form_class()
        if request.POST:
            # Save prefix
            form = form_class(request.POST)
            if form.is_valid():
                for k, v in form.cleaned_data.items():
                    if ((not can_bind_vc and k == "vc") or
                        k == "dual_stack_prefix"):
                        continue
                    setattr(prefix, k, v)
                with self.form_errors(form):
                    prefix.save()
                if not form._errors:
                    self.message_user(
                        request,
                        _("Prefix %(prefix)s has been changed") % {
                            "prefix": prefix})
                    # Process dual-stack linking
                    ds_prefix = form.cleaned_data["dual_stack_prefix"]
                    self.process_dual_stacking(prefix, ds_prefix)
                    return self.response_redirect(
                        "ip:ipam:vrf_index",
                        vrf.id, afi, prefix.prefix)
        else:
            ds_prefix = None
            if prefix.has_transition:
                if afi == "4":
                    ds_prefix = prefix.ipv6_transition.prefix
                elif afi == "6":
                    ds_prefix = prefix.ipv4_transition.prefix
            initial = {
                "asn": prefix.asn.id,
                "state": prefix.state.id,
                "project": prefix.project.id if prefix.project else None,
                "vc": prefix.vc.id if prefix.vc else None,
                "description": prefix.description,
                "dual_stack_prefix": ds_prefix,
                "tags": prefix.tags,
                "tt": prefix.tt,
                "style": prefix.style.id if prefix.style else None
            }
            self.apply_custom_initial(prefix, initial, "ip_prefix")
            form = form_class(initial=initial)
        return self.render(request, "change_prefix.html", vrf=vrf,
            afi=afi, prefix=prefix, form=form)

    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/delete/$",
          url_name="delete_prefix", access="change")
    def view_delete_prefix(self, request, vrf_id, afi, prefix):
        """
        Delete prefix
        """
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        if (afi == "4" and not vrf.afi_ipv4) or (
        afi == "6" and not vrf.afi_ipv6):
            return self.response_forbidden("Invalid AFI")
        if not PrefixAccess.user_can_change(request.user, vrf, afi, prefix):
            return self.response_forbidden()
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        parent = prefix.parent
        if not parent:
            return self.response_forbidden("Cannot delete root prefix")
        if request.POST:
            if "scope" in request.POST and request.POST["scope"][0] in (
            "p", "r"):
                if  request.POST["scope"] == "p":
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

    ##
    ## Return address edit/change form
    ##
    def get_address_form_class(self, vrf, afi, user, create=False):
        class AddressForm(NOCForm):
            address = forms.CharField(label=_("Address"),
                                      help_text=_("IPv%(afi)s address") % {
                                          "afi": afi})
            if create:
                state = forms.ModelChoiceField(
                    label=_("State"),
                    queryset=ResourceState.objects.filter(is_starting=True, is_active=True).order_by("name"),
                    help_text=_("Prefix state")
                )
            else:
                state = forms.ModelChoiceField(label=_("State"),
                    queryset=ResourceState.objects.filter(is_active=True).order_by("name"),
                    help_text=_("Prefix state")
                )
            project = forms.ModelChoiceField(label=_("Project"),
                queryset=Project.objects.order_by("code"),
                help_text=_("Project"),
                required=False
            )
            fqdn = forms.CharField(label=_("FQDN"), validators=[check_fqdn])
            mac = forms.CharField(label=_("MAC"), required=False)
            auto_update_mac = forms.BooleanField(
                label=_("Auto-update MAC"),
                required=False,
                help_text=_("Check to automatically fetch MAC from ARP cache"))
            managed_object = forms.CharField(
                label="Managed Object",
                required=False,
                widget=AutoCompleteTextInput("sa:managedobject:lookup1"),
                help_text=_("Set if address belong to managed object's interface"))
            description = forms.CharField(
                label=_("Description"),
                widget=forms.Textarea,
                required=False)
            tags = forms.CharField(
                label=_("Tags"),
                widget=AutoCompleteTags,
                required=False)
            tt = forms.IntegerField(
                label=_("TT #"),
                required=False,
                help_text=_("Ticket #"))
            style = forms.ModelChoiceField(
                label=_("Style"),
                queryset=Style.objects.filter(is_active=True).order_by("name"),
                                           required=False,
                                           help_text=_("Visual appearance"))

            def clean_address(self):
                address = self.cleaned_data["address"].strip()
                # Validate address
                if afi == "4":
                    check_ipv4(address)
                else:
                    check_ipv6(address)
                    # Check premissions
                if not PrefixAccess.user_can_change(user, vrf, afi, address):
                    raise ValidationError(_("Permission denied"))
                if create:
                    # Check address not exists
                    if Address.objects.filter(vrf=vrf, afi=afi,
                                              address=address).exists():
                        raise ValidationError(_("Address is already exists"))
                return address

            def clean_mac(self):
                if not self.cleaned_data["mac"]:
                    return ""
                try:
                    return MACAddressParameter().clean(self.cleaned_data["mac"].strip())
                except InterfaceTypeError:
                    raise forms.ValidationError("Invalid MAC address")

            def clean_managed_object(self):
                mo_name = self.cleaned_data["managed_object"]
                if mo_name:
                    try:
                        return ManagedObject.objects.get(name=mo_name)
                    except ManagedObject.DoesNotExist:
                        raise ValidationError(_("Invalid Managed Object"))
                else:
                    return ""

        self.customize_form(AddressForm, "ip_address")
        return AddressForm

    ##
    ## Add new address
    ##
    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/add_address/$",
          url_name="add_address", access="change")
    def view_add_address(self, request, vrf_id, afi, prefix):
        # Validate
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        if (afi == "4" and not vrf.afi_ipv4) or (
        afi == "6" and not vrf.afi_ipv6):
            return self.response_forbidden("Invalid AFI")
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        #
        form_class = self.get_address_form_class(vrf, afi, request.user,
                                                 create=True)
        if request.POST:
            # Create address
            form = form_class(request.POST)
            if form.is_valid():
                # Check not in locked range
                if AddressRange.address_is_locked(vrf, afi,
                                                  form.cleaned_data["address"]):
                    self.message_user(request, _(
                        "Address %(address)s is in the locked range") % {
                        "address": form.cleaned_data["address"]})
                    return self.response_redirect("ip:ipam:vrf_index", vrf.id,
                                                  afi, prefix.prefix)
                # Check for collisions
                cv = Address.get_collision(vrf, form.cleaned_data["address"])
                if cv:
                    self.message_user(request, _("Address already present in VRF %(vrf)s") % {
                        "vrf": cv
                    })
                    return self.response_redirect("ip:ipam:vrf_index", vrf.id,
                                                  afi, prefix.prefix)
                # Create address
                a = Address(
                    vrf=vrf,
                    afi=afi,
                    address=form.cleaned_data["address"],
                    state=form.cleaned_data["state"],
                    project=form.cleaned_data["project"],
                    fqdn=form.cleaned_data["fqdn"],
                    mac=form.cleaned_data["mac"],
                    auto_update_mac=form.cleaned_data["auto_update_mac"],
                    managed_object=form.cleaned_data["managed_object"] if form.cleaned_data["managed_object"] else None,
                    description=form.cleaned_data["description"],
                    tags=form.cleaned_data["tags"],
                    tt=form.cleaned_data["tt"],
                    style=form.cleaned_data["style"])
                self.apply_custom_fields(
                    a, form.cleaned_data, "ip_address")
                with self.form_errors(form):
                    a.save()
                if not form._errors:
                    self.message_user(
                        request,
                        _("Address %(address)s has been created") % {
                            "address": a.address})
                    # Redirect depending on submit button pressed
                    if "_continue" in request.POST:
                        return self.response_redirect(
                            "ip:ipam:change_address", vrf.id, afi,
                            form.cleaned_data["address"])
                    if "_addanother" in request.POST:
                        return self.response_redirect(
                            "ip:ipam:add_address", vrf.id, afi,
                            a.prefix.prefix)
                    return self.response_redirect(
                        "ip:ipam:vrf_index",
                        vrf.id, afi, a.prefix.prefix)
        else:
            initial = {
                "state": ResourceState.get_default()
            }
            if "address" in request.GET and (
            (afi == "4" and is_ipv4(request.GET["address"])) or (
            afi == "6" and is_ipv6(request.GET["address"]))):
                # Use address from querystring
                initial["address"] = request.GET["address"]
            else:
                # Find first free address
                p = IP.prefix(prefix.prefix)
                p0 = p.first.iter_address()
                if afi == "4":
                    p0.next()  # Skip network address
                addresses = list(prefix.address_set.order_by("address"))
                if not addresses:
                    # No addresses in block yet.
                    # Get first address
                    initial["address"] = p0.next().address
                else:
                    # Repeat while uses addresses are continuous
                    for a in addresses:
                        a0 = p0.next()
                        if a0.address != a.address:
                            initial["address"] = a0.address
                            break
                    if not initial:
                        # Beyond the last address
                        a0 = p0.next()
                        if IP.prefix(prefix.prefix).contains(a0):
                            a0 = a0.address
                            if afi == "6" or (
                            afi == "4" and a0 != p.last.address):
                                initial["address"] = a0
                    if not initial:
                        self.message_user(request, _("No free addresses"))
                        return self.response_redirect("ip:ipam:vrf_index",
                                                      vrf.id, afi,
                                                      prefix.prefix)
            form = form_class(initial=initial)
        return self.render(request, "change_address.html", vrf=vrf, afi=afi,
                           prefix=prefix, form=form, addresses=None)

    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<address>[^/]+)/change_address/$",
        url_name="change_address", access="change")
    def view_change_address(self, request, vrf_id, afi, address):
        """
        Change address
        """
        # Validate
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        if ((afi == "4" and not vrf.afi_ipv4) or
            (afi == "6" and not vrf.afi_ipv6)):
            return self.response_forbidden("Invalid AFI")
        address = self.get_object_or_404(Address, vrf=vrf, afi=afi,
                                         address=address)
        if not PrefixAccess.user_can_change(request.user, vrf, afi,
                                            address.address):
            return self.response_forbidden()
        prefix = address.prefix
        form_class = self.get_address_form_class(vrf, afi, request.user)
        if request.POST:
            form = form_class(request.POST)
            if form.is_valid():
                # Check not in locked range
                if AddressRange.address_is_locked(vrf, afi,
                                                  form.cleaned_data["address"]):
                    self.message_user(request, _(
                        "Address %(address)s is in the locked range") % {
                        "address": form.cleaned_data["address"]})
                    return self.response_redirect("ip:ipam:vrf_index", vrf.id,
                                                  afi, prefix.prefix)
                # Modify
                managed_object = None
                if ("managed_object" in form.cleaned_data and
                    form.cleaned_data["managed_object"]):
                    managed_object = self.get_object_or_404(ManagedObject,
                                    name=form.cleaned_data["managed_object"])
                address.address = form.cleaned_data["address"]
                address.state = form.cleaned_data["state"]
                address.project = form.cleaned_data["project"]
                address.fqdn = form.cleaned_data["fqdn"]
                address.mac = form.cleaned_data["mac"]
                address.auto_update_mac = form.cleaned_data["auto_update_mac"]
                address.managed_object = managed_object
                address.description = form.cleaned_data["description"]
                address.tags = form.cleaned_data["tags"]
                address.tt = form.cleaned_data["tt"]
                address.style = form.cleaned_data["style"]
                self.apply_custom_fields(
                    address, form.cleaned_data, "ip_address")
                with self.form_errors(form):
                    address.save()
                if not form._errors:
                    self.message_user(
                        request,
                        _("Address %(address)s changed") % {
                            "address": address.address})
                    if "_continue" in request.POST:
                        return self.response_redirect(
                            "ip:ipam:change_address",
                            vrf.id, afi, form.cleaned_data["address"])
                    if "_addanother" in request.POST:
                        return self.response_redirect(
                            "ip:ipam:add_address",
                            vrf.id, afi, prefix.prefix)
                    return self.response_redirect(
                        "ip:ipam:vrf_index",
                        vrf.id, afi, address.prefix.prefix)
        else:
            initial = {
                "address": address.address,
                "state": address.state,
                "project": address.project.id if address.project else None,
                "fqdn": address.fqdn,
                "mac": address.mac,
                "auto_update_mac": address.auto_update_mac,
                "description": address.description,
                "tags": address.tags,
                "tt": address.tt,
                "style": address.style.id if address.style else None
            }
            if address.managed_object:
                initial["managed_object"] = address.managed_object.name
            self.apply_custom_initial(address, initial, "ip_address")
            form = form_class(initial=initial)
        return self.render(
            request, "change_address.html", vrf=vrf, afi=afi,
            prefix=prefix, form=form, address=address)

    @view(
        url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<address>[^/]+)/delete_address/$",
        url_name="delete_address", access="change")
    def view_delete_address(self, request, vrf_id, afi, address):
        """
        Delete address
        """
        # Validate
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        if ((afi == "4" and not vrf.afi_ipv4) or
            (afi == "6" and not vrf.afi_ipv6)):
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
        # Get activator name
        activator_name = r[0].managed_object.activator.name
        # Get addresses to ping
        addresses = [a.address for a in self.get_prefix_spot(p, sep=False)]
        # Run Map/Reduce task
        t = ReduceTask.create_task(["SAE"], "pyrule:get_single_result", {},
                                          "ping_check",
                {"activator_name": activator_name, "addresses": addresses}, 60)
        return self.render_json(t.id)

    @view(
        url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/ping_check/(?P<task_id>\d+)/$",
        url_name="ping_check_task",
        access="change")
    def view_ping_check_task(self, request, vrf_id, afi, prefix, task_id):
        """
        Ping check task result
        """
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        p = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        task = self.get_object_or_404(ReduceTask, id=int(task_id))
        try:
            result = task.get_result(block=False)
        except ReduceTask.NotReady:
            return self.render_json(None)  # Waiting
        r = {}
        for s in result:
            r[s["ip"]] = s["status"]
        return self.render_json(r)

    class RebaseForm(NOCForm):
        vrf = forms.ModelChoiceField(label="VRF",
            queryset=VRF.objects.all())
        to_prefix = forms.CharField(label="Rebase to prefix")

        def __init__(self, prefix, data=None):
            initial = None if data else {"to_prefix": prefix.prefix}
            super(IPAMAppplication.RebaseForm, self).__init__(
                data, initial=initial)
            self.prefix = prefix

        def clean_to_prefix(self):
            to_prefix = self.cleaned_data["to_prefix"]
            check_prefix(to_prefix)
            p0 = IP.prefix(self.prefix.prefix)
            p1 = IP.prefix(to_prefix)
            if p0 == p1 and self.cleaned_data["vrf"] == self.prefix.vrf:
                raise forms.ValidationError("Cannot rebase prefix to self")
            if p0.afi != p1.afi:
                raise forms.ValidationError("Cannot change address family during rebase")
            if p0.mask < p1.mask:
                raise forms.ValidationError("Cannot rebase to prefix of lesser size")
            return to_prefix

    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/rebase/$",
        url_name="rebase", access="rebase")
    def view_rebase(self, request, vrf_id, afi, prefix):
        vrf = self.get_object_or_404(VRF,id=int(vrf_id))
        prefix = self.get_object_or_404(
            Prefix, vrf=vrf, afi=afi, prefix=prefix)
        if request.POST:
            form = self.RebaseForm(prefix, request.POST)
            if form.is_valid():
                # Rebase prefix
                new_prefix = prefix.rebase(
                    form.cleaned_data["vrf"],
                    form.cleaned_data["to_prefix"])
                self.message_user(request,
                    _(u"Prefix %(old_prefix)s is rebased to %(new_prefix)s") % {
                    "old_prefix": prefix,
                    "new_prefix": form.cleaned_data["to_prefix"]})
                return self.response_redirect("ip:ipam:vrf_index",
                    new_prefix.vrf.id, afi, new_prefix.prefix)
        else:
            form = self.RebaseForm(prefix)
        return self.render(request,
            "rebase.html", vrf=vrf, afi=afi, prefix=prefix,
            rebase_form=form)

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
