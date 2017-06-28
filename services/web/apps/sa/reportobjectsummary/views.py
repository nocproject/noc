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
            query = """SELECT profile_name,COUNT(*) FROM sa_managedobject
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
            query = """SELECT d.name,profile_name,COUNT(*)
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
            query = """select sam.profile_name, sama.value,count(value)
                    from sa_managedobject sam join  sa_managedobjectattribute sama on (sam.id=sama.managed_object_id)
                    where sama.key='platform' %s%s group by 1,2 order by count(value) desc;""" % wr_and

        elif report_type == "version":
            columns = [_("Platform"), _("Version")]
            query = """select sam.profile_name, sama.value,count(value)
                    from sa_managedobject sam join sa_managedobjectattribute sama on (sam.id=sama.managed_object_id)
                    where sama.key='version' %s%s group by 1,2 order by count(value) desc;""" % wr_and

        else:
            raise Exception("Invalid report type: %s" % report_type)
        for r, t in report_types:
            if r == report_type:
                title = self.title+": "+t
                break
        columns += [TableColumn(_("Quantity"), align="right", total="sum", format="integer")]
        return self.from_query(title=title, columns=columns, query=query, enumerate=True)
