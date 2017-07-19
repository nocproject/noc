# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python Modules
import csv
import subprocess
# Third-party modules
import six
# NOC Modules
from noc.lib.app.application import Application, HasPerm, view
from noc.core.ip import IP, IPv4
from noc.ip.models.address import Address
from noc.ip.models.prefix import Prefix
from noc.ip.models.vrf import VRF
from noc.lib.forms import *
from noc.config import config
from noc.core.translation import ugettext as _


#
# IP Block tools
#
class ToolsAppplication(Application):
    title = _("Tools")

    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+?/\d+)/$",
          url_name="index",
          access=HasPerm("view"))
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
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi,
                                        prefix=prefix)
        if not prefix.can_change(request.user):
            return self.response_forbidden(_("Permission denied"))
        return self.render(request, "index.html", vrf=vrf, afi=afi,
                           prefix=prefix,
                           upload_ips_axfr_form=self.AXFRForm())

    @view(
        url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/download_ip/$",
        url_name="download_ip",
        access=HasPerm("view"))
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
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi,
                                        prefix=prefix)
        if not prefix.can_change(request.user):
            return self.response_forbidden(_("Permission denied"))
        out = six.StringIO()
        writer = csv.writer(out)
        writer.writerow(
            ["address", "fqdn", "mac", "description", "tt", "tags"])
        for a in prefix.nested_address_set.order_by("address"):
            writer.writerow(
                [a.address, a.fqdn, a.mac, to_utf8(a.description), a.tt,
                 a.tags])
        return self.render_response(out.getvalue(),
                                    content_type="text/csv")

    class AXFRForm(NOCForm):
        """
        Zone import form
        """
        ns = forms.CharField(label=_("NS"), help_text=_(
            "Name server IP address. NS must have zone transfer enabled for NOC host"))
        zone = forms.CharField(label=_("Zone"),
                               help_text=_("DNS Zone name to transfer"))
        source_address = forms.IPAddressField(label=_("Source Address"),
                                              required=False,
                                              help_text=_(
                                                  "Source address to issue zone transfer"))

    @view(
        url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/upload_axfr/$",
        url_name="upload_axfr",
        access=HasPerm("view"))
    def view_upload_axfr(self, request, vrf_id, afi, prefix):
        """
        Import via zone transfer
        :param request:
        :param vrf_id:
        :param afi:
        :param prefix:
        :return:
        """

        def upload_axfr(data):
            p = IP.prefix(prefix.prefix)
            count = 0
            for row in data:
                row = row.strip()
                if row == "" or row.startswith(";"):
                    continue
                row = row.split()
                if len(row) != 5 or row[2] != "IN" or row[3] != "PTR":
                    continue
                if row[3] == "PTR":
                    # @todo: IPv6
                    x = row[0].split(".")
                    ip = "%s.%s.%s.%s" % (x[3], x[2], x[1], x[0])
                    fqdn = row[4]
                    if fqdn.endswith("."):
                        fqdn = fqdn[:-1]
                # Leave only addresses residing into "prefix"
                # To prevent uploading to not-owned blocks
                if not p.contains(IPv4(ip)):
                    continue
                a, changed = Address.objects.get_or_create(vrf=vrf,
                                                           afi=afi,
                                                           address=ip)
                if a.fqdn != fqdn:
                    a.fqdn = fqdn
                    changed = True
                if changed:
                    a.save()
                    count += 1
            return count

        vrf = self.get_object_or_404(VRF, id=int(vrf_id))
        prefix = self.get_object_or_404(Prefix, vrf=vrf, afi=afi,
                                        prefix=prefix)
        if not prefix.can_change(request.user):
            return self.response_forbidden(_("Permission denined"))
        if request.POST:
            form = self.AXFRForm(request.POST)
            if form.is_valid():
                opts = []
                if form.cleaned_data["source_address"]:
                    opts += ["-b", form.cleaned_data["source_address"]]
                pipe = subprocess.Popen(
                    [config.path.dig] + opts + [
                        "axfr", "@%s" % form.cleaned_data["ns"], form.cleaned_data["zone"]],
                    shell=False, stdout=subprocess.PIPE).stdout
                data = pipe.read()
                pipe.close()
                count = upload_axfr(data.split("\n"))
                self.message_user(request, _(
                    "%(count)s IP addresses uploaded via zone transfer") % {
                                      "count": count})
                return self.response_redirect("ip:ipam:vrf_index",
                                              vrf.id, afi,
                                              prefix.prefix)
        else:
            form = self.AXFRForm()
        return self.render(request, "index.html", vrf=vrf, afi=afi,
                           prefix=prefix,
                           upload_ips_axfr_form=form)
