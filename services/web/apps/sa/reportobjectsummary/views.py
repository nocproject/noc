# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------
# Objects Summary Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
# Third-party modules
from django import forms
# NOC modules
from noc.sa.models.profile import Profile
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.lib.app.simplereport import SimpleReport, TableColumn, PredefinedReport
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _
#
#
#
report_types = [
    ("profile", _("By Profile")),
    ("domain", _("By Administrative Domain")),
    ("domain-profile", _("By Administrative Domain and Profile")),
    ("tag", _("By Tags")),
    ("platform", _("By Platform")),
    ("version", _("By Version"))
]


class ReportForm(forms.Form):
    report_type = forms.ChoiceField(label=_("Report Type"), choices=report_types)
#
#
#


class ReportObjectsSummary(SimpleReport):
    title = _("Managed Objects Summary")
    form = ReportForm
    predefined_reports = {
        "profile": PredefinedReport(
            _("Managed Objects Summary (profile)"), {
                "report_type": "profile"
            }
        ),
        "domain": PredefinedReport(
            _("Managed Objects Summary (domain)"), {
                "report_type": "domain"
            }
        ),
        "domain-profile": PredefinedReport(
            _("Managed Objects Summary (domain-profile)"), {
                "report_type": "domain-profile"
            }
        ),
        "tag": PredefinedReport(
            _("Managed Objects Summary (tag)"), {
                "report_type": "tag"
            }
        ),
        "platform": PredefinedReport(
            _("Managed Objects Summary (platform)"), {
                "report_type": "platform"
            }
        ),
        "version": PredefinedReport(
            _("Managed Objects Summary (version)"), {
                "report_type": "version"
            }
        )

    }

    def get_data(self, request, report_type, **kwargs):
        wr = ("", "",)
        wr_and = ("", "",)
        wr_and2 = ("", "",)
        platform = {str(p["_id"]): p["name"] for p in Platform.objects.all().as_pymongo().scalar("id", "name")}
        version = {str(p["_id"]): p["version"] for p in Firmware.objects.all().as_pymongo().scalar("id", "version")}
        profile = {str(p["_id"]): p["name"] for p in Profile.objects.all().as_pymongo().scalar("id", "name")}

        if not request.user.is_superuser:
            ad = tuple(UserAccess.get_domains(request.user))
            wr = ("WHERE administrative_domain_id in ", ad)
            wr_and = ("AND sam.administrative_domain_id in ", ad)
            wr_and2 = ("AND administrative_domain_id in ", ad)
            if len(ad) == 1:
                wr = ("WHERE administrative_domain_id in (%s)" % ad, "")
                wr_and = ("AND sam.administrative_domain_id in (%s)" % ad, "")
                wr_and2 = ("AND administrative_domain_id in (%s)" % ad, "")
        # By Profile
        if report_type == "profile":
            columns = [_("Profile")]
            query = """SELECT profile,COUNT(*) FROM sa_managedobject
                    %s%s GROUP BY 1 ORDER BY 2 DESC""" % wr
        # By Administrative Domain
        elif report_type == "domain":
            columns = [_("Administrative Domain")]
            query = """SELECT a.name,COUNT(*)
                  FROM sa_managedobject o JOIN sa_administrativedomain a ON (o.administrative_domain_id=a.id)
                  %s%s
                  GROUP BY 1
                  ORDER BY 2 DESC""" % wr
        # By Profile and Administrative Domains
        elif report_type == "domain-profile":
            columns = [_("Administrative Domain"), _("Profile")]
            query = """SELECT d.name,profile,COUNT(*)
                    FROM sa_managedobject o JOIN sa_administrativedomain d ON (o.administrative_domain_id=d.id)
                    %s%s
                    GROUP BY 1,2
                    """ % wr
        # By tags
        elif report_type == "tag":
            columns = [_("Tag")]
            query = """
              SELECT t.tag, COUNT(*)
              FROM (
                SELECT unnest(tags) AS tag
                FROM sa_managedobject
                WHERE
                  tags IS NOT NULL
                  %s%s
                  AND array_length(tags, 1) > 0
                ) t
              GROUP BY 1
              ORDER BY 2 DESC;
            """ % wr_and2
        elif report_type == "platform":
            columns = [_("Platform"), _("Profile")]
            query = """select sam.profile, sam.platform, COUNT(platform)
                    from sa_managedobject sam %s%s group by 1,2 order by count(platform) desc;""" % wr

        elif report_type == "version":
            columns = [_("Profile"), _("Version")]
            query = """select sam.profile, sam.version, COUNT(version)
                    from sa_managedobject sam %s%s group by 1,2 order by count(version) desc;""" % wr

        else:
            raise Exception("Invalid report type: %s" % report_type)
        for r, t in report_types:
            if r == report_type:
                title = self.title+": "+t
                break
        columns += [TableColumn(_("Quantity"), align="right", total="sum", format="integer")]

        cursor = self.cursor()
        cursor.execute(query, ())
        data = []
        for c in cursor.fetchall():
            if report_type == "profile":
                data += [(profile.get(c[0]), c[1])]
            elif report_type == "domain-profile":
                data += [(c[0], profile.get(c[1]), c[2])]
            elif report_type == "platform":
                data += [(profile.get(c[0]), platform.get(c[1]), c[2])]
            elif report_type == "version":
                data += [(profile.get(c[0]), version.get(c[1]), c[2])]
            else:
                data += [c]

        return self.from_dataset(title=title, columns=columns, data=data, enumerate=True)
