# ---------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python Modules
import csv
import dns
from io import StringIO

# Third-party modules
from django import forms

# NOC Modules
from noc.lib.app.application import Application, HasPerm, view
from noc.core.ip import IP, IPv4
from noc.ip.models.address import Address
from noc.ip.models.prefix import Prefix
from noc.ip.models.vrf import VRF
from noc.core.forms import NOCForm
from noc.core.translation import ugettext as _


#
# IP Block tools
#
class ToolsAppplication(Application):
    title = _("Tools")

    @view(
        url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+?/\d+)/$",
        url_name="index",
        access=HasPerm("view"),
    )
    def view_index(self, request, vrf_id, afi, prefix):
        """
        An index of tools available for block
        :param request:
        :param vrf_id:
        :param afi:
        :param prefix:
        :return:
        """
        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        if not prefix.can_change(request.user):
            return self.response_forbidden(_("Permission denied"))
        return self.render(
            request,
            "index.html",
            vrf=vrf,
            afi=afi,
            prefix=prefix,
            upload_ips_axfr_form=self.AXFRForm(),
        )

    @view(
        url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/download_ip/$",
        url_name="download_ip",
        access=HasPerm("view"),
    )
    def view_download_ip(self, request, vrf_id, afi, prefix):
        """
        Download block's allocated IPs in CSV format
        Columns are: ip,fqdn,description,tt
        :param request:
        :param vrf_id:
        :param afi:
        :param prefix:
        :return:
        """

        def to_utf8(x):
            if x:
                return x.encode("utf8")
            else:
                return ""

        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        if not prefix.can_change(request.user):
            return self.response_forbidden(_("Permission denied"))
        out = StringIO()
        writer = csv.writer(out)
        writer.writerow(["address", "fqdn", "mac", "description", "tt", "tags"])
        for a in prefix.nested_address_set.order_by("address"):
            writer.writerow([a.address, a.fqdn, a.mac, to_utf8(a.description), a.tt, a.labels])
        return self.render_response(out.getvalue(), content_type="text/csv")

    class AXFRForm(NOCForm):
        """
        Zone import form
        """

        ns = forms.CharField(
            label=_("NS"),
            help_text=_("Name server IP address. NS must have zone transfer enabled for NOC host"),
        )
        zone = forms.CharField(label=_("Zone"), help_text=_("DNS Zone name to transfer"))
        source_address = forms.GenericIPAddressField(
            label=_("Source Address"),
            required=False,
            protocol="IPv4",
            help_text=_("Source address to issue zone transfer"),
        )

    @view(
        url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/upload_axfr/$",
        url_name="upload_axfr",
        access=HasPerm("view"),
    )
    def view_upload_axfr(self, request, vrf_id, afi, prefix):
        """
        Import via zone transfer
        :param request:
        :param vrf_id:
        :param afi:
        :param prefix:
        :return:
        """

        def resolve_dns(name):
            types = ["A", "AAAA", "PTR"]
            for type in types:
                try:
                    results = dns.resolver.resolve(qname=name, rdtype=type)
                except dns.exception.DNSException as e:
                    print(f"Dns resolution Error: {e} ({name} {type})")
                    continue
                if results:
                    return results

        def upload_axfr(data, zone):
            p = IP.prefix(prefix.prefix)
            count = 0
            zz = zone + "."
            lz = len(zz)
            for host in data:
                if str(host) == "@":
                    continue
                r_host = f"{str(host)}.{zone}"
                A_records = resolve_dns(r_host)
                if not A_records:
                    continue
                for item in A_records:
                    if A_records.rdtype.name in ("A", "AAAA"):
                        name = r_host
                    if A_records.rdtype.name == "PTR":
                        name = str(item)
                        if name.endswith(zz):
                            name = name[:-lz]
                        if name.endswith("."):
                            name = name[:-1]
                        # @todo: IPv6
                        if "." in r_host:
                            address = ".".join(reversed(r_host.split(".")[:4]))
                        fqdn = str(item)
                        if fqdn.endswith("."):
                            fqdn = fqdn[:-1]
                # Leave only addresses residing into "prefix"
                # To prevent uploading to not-owned blocks
                if not p.contains(IPv4(address)):
                    continue
                a, changed = Address.objects.get_or_create(vrf=vrf, afi=afi, address=address)
                if a.fqdn != fqdn:
                    a.fqdn = fqdn
                    changed = True
                if changed:
                    a.save()
                    count += 1
            return count

        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        if not prefix.can_change(request.user):
            return self.response_forbidden(_("Permission denined"))
        if request.POST:
            form = self.AXFRForm(request.POST)
            if form.is_valid():
                try:
                    data = dns.zone.from_xfr(
                        dns.query.xfr(
                            str(form.cleaned_data["ns"]).rstrip("."),
                            form.cleaned_data["zone"],
                            lifetime=5.0,
                        )
                    )
                except dns.exception.Timeout as e:
                    self.message_user(request, e)
                    return
                else:
                    count = upload_axfr(data, form.cleaned_data["zone"])
                self.message_user(
                    request,
                    _("%(count)s IP addresses uploaded via zone transfer") % {"count": count},
                )
                return self.response_redirect("ip:ipam:vrf_index", vrf.id, afi, prefix.prefix)
        else:
            form = self.AXFRForm()
        return self.render(
            request, "index.html", vrf=vrf, afi=afi, prefix=prefix, upload_ips_axfr_form=form
        )
