# ---------------------------------------------------------------------
# Failed Scripts Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django import forms
from pymongo import ReadPreference

# NOC modules
from noc.services.web.app.simplereport import SimpleReport, SectionRow, PredefinedReport
from noc.services.web.app.reportdatasources.base import ReportModelFilter
from noc.services.web.app.reportdatasources.report_discoveryresult import ReportDiscoveryResult
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.discoveryid import DiscoveryID
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _


class ReportFilterApplication(SimpleReport):
    title = _("Failed Discovery")

    predefined_reports = {
        pname: PredefinedReport(_("Failed Discovery (pool)") + f": {pname}", {"pool": str(pid)})
        for pid, pname in (list(Pool.objects.order_by("name").scalar("id", "name")) + [("", "ALL")])
    }

    def get_form(self):
        class ReportForm(forms.Form):
            pool = forms.ChoiceField(
                label=_("Managed Objects Pool"),
                required=False,
                help_text="Pool for choice",
                choices=list(Pool.objects.order_by("name").scalar("id", "name"))
                + [(None, "-" * 9)],
            )
            resource_group = forms.ChoiceField(
                label=_("Managed Objects Group (Selector)"),
                required=False,
                help_text="Group for choice",
                choices=list(ResourceGroup.objects.order_by("name").scalar("id", "name"))
                + [(None, "-" * 9)],
            )

        return ReportForm

    @staticmethod
    def decode_problem(problems):
        """

        :param problems:
        :type problems: collections.namedtuple
        :return:
        """
        decode_map = {
            "Cannot detect profile": "SNMP Timeout",
            "Remote error code 10000": "CLI Problem: Unspecified CLI error",
            "Remote error code 10001": "CLI Problem: Authentication failed",
            "Remote error code 10002": "CLI Problem: No super command defined",
            "Remote error code 10003": "CLI Problem: No super privileges",
            "Remote error code 10004": "CLI Problem: SSH Protocol error",
            "Remote error code 10005": "CLI Problem: Connection refused",
            "Remote error code 10200": "SNMP Problem",
            "Remote error code 10201": "SNMP Timeout",
            "Remote error code 599": "HTTP Error: Connection Timeout",
            "Remote error code 1": "Adapter failed",
        }

        decode, message = None, ""
        if not problems:
            return message
        for index, message in enumerate(problems):
            if not message:
                continue
            decode = decode_map.get(str(message))
            break
        if decode is None:
            decode = message
        return decode

    def get_data(self, request, pool=None, resource_group=None, report_type=None, **kwargs):

        data = []
        columns, columns_desr = [], []
        r_map = [
            (_("Not Available"), "2is1.3isp1.3is1"),
            (_("Failed to guess CLI credentials"), "2is1.6is1.3isp0.2isp1"),
            (_("Failed to guess SNMP community"), "2is1.6is1.3isp1.3is2.1isp1"),
        ]
        for x, y in r_map:
            columns += [y]
            columns_desr += [x]
        mos = ManagedObject.objects.filter()
        if pool:
            pool = Pool.get_by_id(pool)
            mos = mos.filter(pool=pool)
            data += [SectionRow(name=pool.name)]
        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        mos = list(mos.values_list("id", flat=True).order_by("id"))
        mos_s = set(mos)
        report = ReportModelFilter()
        result = report.proccessed(",".join(columns))

        mo_hostname = {
            val["object"]: val["hostname"]
            for val in DiscoveryID._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .find({"hostname": {"$exists": 1}}, {"object": 1, "hostname": 1})
        }
        d_result = ReportDiscoveryResult(sync_ids=mos)
        d_result = d_result.get_dictionary()
        for col in columns:
            for mo_id in result[col.strip()].intersection(mos_s):
                mo = ManagedObject.get_by_id(mo_id)
                problem = self.decode_problem(d_result.get(mo_id))
                if not problem and mo_id not in d_result:
                    problem = "Discovery disabled"
                data += [
                    (
                        mo.name,
                        mo.address,
                        mo.administrative_domain.name,
                        mo.profile.name,
                        mo_hostname.get(mo.id, ""),
                        mo.auth_profile if mo.auth_profile else "",
                        mo.auth_profile.user if mo.auth_profile else mo.user,
                        mo.auth_profile.snmp_ro if mo.auth_profile else mo.snmp_ro,
                        _("No") if not mo.get_status() else _("Yes"),
                        columns_desr[columns.index(col)],
                        problem,
                    )
                ]
        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"),
                _("Address"),
                _("Administrative Domain"),
                _("Profile"),
                _("Hostname"),
                _("Auth Profile"),
                _("Username"),
                _("SNMP Community"),
                _("Avail"),
                _("Error"),
                _("Error Detail"),
            ],
            data=data,
        )
