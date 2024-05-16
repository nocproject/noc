# ---------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python Modules
import csv
import dns
import orjson
from io import StringIO

# Third-party modules
from django import forms
from django.http import HttpResponse

# NOC Modules
from noc.services.web.base.application import Application, HasPerm, view
from noc.core.ip import IP, IPv4, IPv6
from noc.core.validators import is_ipv4, is_ipv6
from noc.core.forms import NOCForm
from noc.core.translation import ugettext as _
from noc.ip.models.address import Address
from noc.ip.models.prefix import Prefix
from noc.ip.models.vrf import VRF
from noc.ip.models.addressprofile import AddressProfile


#
# IP Block tools
#
class ToolsApplication(Application):
    title = _("Tools")
    extra_permissions = ["download_ip", "upload_axfr", "view"]

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
        access=HasPerm("download_ip"),
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
        writer.writerow(["address", "name", "fqdn", "mac", "description", "tt", "tags"])
        for a in prefix.nested_address_set.order_by("address"):
            writer.writerow(
                [a.address, a.name, a.fqdn, a.mac, to_utf8(a.description), a.tt, a.labels]
            )
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

    @view(
        url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/upload_axfr/$",
        url_name="upload_axfr",
        access=HasPerm("upload_axfr"),
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

        def upload_axfr(data, zone):
            p = IP.prefix(prefix.prefix)
            create = 0
            change = 0
            zz = zone + "."
            lz = len(zz)
            ap = AddressProfile.objects.filter(name="default").first()
            for row in data.splitlines():
                row = row.strip().split()
                if len(row) != 5 or row[3] not in ("A", "AAAA", "PTR"):
                    continue
                if row[3] == "PTR":
                    host = dns.name.from_text(f"{row[0]}.{zone}.")
                    ip = dns.reversename.to_address(host)
                    fqdn = row[4]
                    if fqdn.endswith("."):
                        fqdn = fqdn[:-1]
                elif row[3] in ("A", "AAAA"):
                    fqdn = row[0]
                    if fqdn.endswith(zz):
                        fqdn = fqdn[:-lz]
                    if fqdn.endswith("."):
                        fqdn = fqdn[:-1]
                    ip = row[4]
                # Leave only addresses residing into "prefix"
                # To prevent uploading to not-owned blocks
                if (
                    is_ipv4(ip)
                    and not p.contains(IPv4(ip))
                    or is_ipv6(ip)
                    and not p.contains(IPv6(ip))
                ):
                    continue
                a = Address.objects.filter(vrf=vrf, afi=afi, address=ip).first()
                if a:
                    if a.fqdn != fqdn:
                        a.fqdn = fqdn
                        a.name = fqdn
                        a.save()
                        change += 1
                else:
                    # Not found
                    a = Address(
                        vrf=vrf,
                        afi=afi,
                        address=ip,
                        profile=ap,
                        fqdn=fqdn,
                        name=fqdn,
                        description="Imported from %s zone" % zone,
                    )
                    a.save()
                    create += 1
            return create, change

        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        if not prefix.can_change(request.user):
            return self.response_forbidden(_("Permission denined"))
        body = orjson.loads(request.body)
        if not is_ipv4(body["ns"]) and not is_ipv6(body["ns"]):
            try:
                answer = dns.resolver.resolve(qname=body["ns"], rdtype="A", lifetime=5.0)
                ip = answer[0].address
            except dns.exception.DNSException as e:
                self.error(f"Resolv Error: {e}")
                return HttpResponse(e, status=500)
        else:
            ip = body["ns"]
        try:
            _zone = dns.zone.from_xfr(
                dns.query.xfr(
                    ip,
                    body["zone"],
                    lifetime=5.0,
                )
            )
            data = "\n".join(
                _zone[z_node].to_text(z_node)
                for z_node in _zone.nodes.keys()
                if "@" not in _zone[z_node].to_text(z_node)
            )
        except dns.exception.DNSException as e:
            self.error(f"DNS Error: {e}")
            return HttpResponse(e, status=400)
        except Exception as e:
            self.error(f"Other Error: {e}")
            return HttpResponse(e, status=500)

        if data:
            create, change = upload_axfr(data, body["zone"])
            return HttpResponse(
                _(
                    f"Created: {create} and Changed: {change} IP addresses uploaded via zone transfer."
                )
            )
        return HttpResponse("No DNS Zone", status=404)
