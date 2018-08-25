# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.reportobjectdetail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import datetime
import csv
import StringIO
# Third-party modules
import xlsxwriter
from django.http import HttpResponse
# NOC modules
from noc.main.models.pool import Pool
from noc.lib.app.extapplication import ExtApplication, view
from noc.lib.app.reportdatasources.base import ReportModelFilter
from noc.lib.app.reportdatasources.report_objectlinkcount import ReportObjectLinkCount
from noc.lib.app.reportdatasources.report_objectifacestypestat import ReportObjectIfacesTypeStat
from noc.lib.app.reportdatasources.report_container import ReportContainer
from noc.lib.app.reportdatasources.report_discoveryresult import ReportDiscoveryResult
from noc.lib.app.reportdatasources.report_objectifacesstatusstat import ReportObjectIfacesStatusStat
from noc.lib.app.reportdatasources.report_objectcaps import ReportObjectCaps
from noc.lib.app.reportdatasources.report_objecthostname import ReportObjectsHostname1
from noc.lib.app.reportdatasources.report_objectconfig import ReportObjectConfig
from noc.sa.interfaces.base import StringParameter, BooleanParameter
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.objectstatus import ObjectStatus
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.profile import Profile
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.vendor import Vendor
from noc.inv.models.firmware import Firmware
from noc.inv.models.platform import Platform
from noc.core.translation import ugettext as _

logger = logging.getLogger(__name__)


class ReportAdPath(object):
    """
    Return AD path
    """

    def __init__(self):
        self.out = self.load()

    def load(self):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""SELECT ad.id, ad.name, r.name, ad2.name
                          FROM sa_administrativedomain r
                          JOIN sa_administrativedomain ad ON ad.parent_id = r.id
                          JOIN sa_administrativedomain ad2 ON r.parent_id = ad2.id;
                """)
        return {r[1]: (r[2], r[3]) for r in cursor}

    def __getitem__(self, item):
        return self.out.get(item, [])


class ReportObjectDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Object Detail")
    title = _("Object Detail")

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    def get_report_object(self, user=None, is_managed=None, adm=None, selector=None,
                          pool=None, segment=None, ids=None):
        mos = ManagedObject.objects.filter()
        if user.is_superuser and not adm and not selector and not segment:
            mos = ManagedObject.objects.filter()
        if ids:
            mos = ManagedObject.objects.filter(id__in=[ids])
        if is_managed is not None:
            mos = ManagedObject.objects.filter(is_managed=is_managed)
        if pool:
            p = Pool.get_by_name(pool or "default")
            mos = mos.filter(pool=p)
        if not user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(user))
        if adm:
            ads = AdministrativeDomain.get_nested_ids(int(adm))
            mos = mos.filter(administrative_domain__in=ads)
        if selector:
            selector = ManagedObjectSelector.get_by_id(int(selector))
            mos = mos.filter(selector.Q)
        if segment:
            segment = NetworkSegment.objects.filter(id=segment).first()
            if segment:
                mos = mos.filter(segment__in=segment.get_nested_ids())
        return mos

    @view("^download/$", method=["GET"], access="launch", api=True,
          validate={
              "administrative_domain": StringParameter(required=False),
              "pool": StringParameter(required=False),
              "segment": StringParameter(required=False),
              "selector": StringParameter(required=False),
              "ids": StringParameter(required=False),
              "detail_stat": StringParameter(required=False),
              "is_managed": BooleanParameter(required=False),
              "avail_status": BooleanParameter(required=False),
              "columns": StringParameter(required=False),
              "o_format": StringParameter(choices=["csv", "xlsx"])})
    def api_report(self, request, o_format, is_managed=None,
                   administrative_domain=None, selector=None, pool=None,
                   segment=None, avail_status=False, columns=None, ids=None,
                   detail_stat=None):
        def row(row):
            def qe(v):
                if v is None:
                    return ""
                if isinstance(v, unicode):
                    return v.encode("utf-8")
                elif isinstance(v, datetime.datetime):
                    return v.strftime("%Y-%m-%d %H:%M:%S")
                elif not isinstance(v, str):
                    return str(v)
                else:
                    return v

            return [qe(x) for x in row]

        def translate_row(row, cmap):
            return [row[i] for i in cmap]

        type_columns = ["Up/10G", "Up/1G", "Up/100M", "Down/-", "-"]

        cols = [
            "id",
            "object_name",
            "object_address",
            "object_hostname",
            "object_status",
            "profile_name",
            "object_profile",
            "object_vendor",
            "object_platform",
            "object_version",
            "object_serial",
            "auth_profile",
            "avail",
            "admin_domain",
            "container",
            "segment",
            "phys_interface_count",
            "link_count",
            "last_config_ts"
            # "discovery_problem"
            # "object_tags"
            # "sorted_tags"
            # "object_caps"
            # "interface_type_count"
        ]

        header_row = [
            "ID",
            "OBJECT_NAME",
            "OBJECT_ADDRESS",
            "OBJECT_HOSTNAME",
            "OBJECT_STATUS",
            "PROFILE_NAME",
            "OBJECT_PROFILE",
            "OBJECT_VENDOR",
            "OBJECT_PLATFORM",
            "OBJECT_VERSION",
            "OBJECT_SERIAL",
            "AUTH_PROFILE",
            "AVAIL",
            "ADMIN_DOMAIN",
            "CONTAINER",
            "SEGMENT",
            "PHYS_INTERFACE_COUNT",
            "LINK_COUNT",
            "LAST_CONFIG_TS"
        ]
        # "DISCOVERY_PROBLEM"
        # "ADM_PATH
        # "DISCOVERY_PROBLEM"
        # "OBJECT_TAGS"
        # "SORTED_TAGS"
        # "OBJECT_CAPS"
        # "INTERFACE_TYPE_COUNT"

        if columns:
            cmap = []
            for c in columns.split(","):
                try:
                    cmap += [cols.index(c)]
                except ValueError:
                    continue
        else:
            cmap = list(range(len(cols)))

        r = [translate_row(header_row, cmap)]
        if "interface_type_count" in columns.split(","):
            r[-1].extend(type_columns)

        mos = self.get_report_object(request.user, is_managed, administrative_domain,
                                     selector, pool, segment, ids)

        mos_id = tuple(mos.order_by("id").values_list("id", flat=True))
        mos_filter = None
        if detail_stat:
            ref = ReportModelFilter()
            ids = ref.proccessed(detail_stat).values()
            mos_filter = set(mos_id).intersection(ids[0])
            mos_id = sorted(mos_filter)
        avail = {}
        if "avail" in columns.split(","):
            avail = ObjectStatus.get_statuses(mos_id)
        link_count = iter(ReportObjectLinkCount(mos_id))
        iface_count = iter(ReportObjectIfacesTypeStat(mos_id))
        container_lookup = iter(ReportContainer(mos_id))
        iss = iter(ReportObjectIfacesStatusStat(mos_id))
        hn = iter(ReportObjectsHostname1(mos_id))
        rc = iter(ReportObjectConfig(mos_id))
        # ccc = iter(ReportObjectCaps(mos_id))
        if "adm_path" in columns.split(","):
            ad_path = ReportAdPath()
            r[-1].extend([_("ADM_PATH1"), _("ADM_PATH1"), _("ADM_PATH1")])
        if "object_caps" in columns.split(","):
            object_caps = ReportObjectCaps(mos_id)
            caps_columns = object_caps.ATTRS.values()
            ccc = iter(object_caps)
            r[-1].extend(caps_columns)
        if "object_tags" in columns.split(","):
            r[-1].extend([_("OBJECT_TAGS")])
        if "sorted_tags" in columns.split(","):
            tags = set()
            for s in ManagedObject.objects.filter().exclude(
                    tags=None).values_list('tags', flat=True).distinct():
                tags.update(set(s))
            tags_o = sorted([t for t in tags if "{" not in t])
            r[-1].extend(tags_o)
        if "discovery_problem" in columns.split(","):
            discovery_result = ReportDiscoveryResult(mos_id)
            discovery_result.safe_output = True
            discovery_result.unknown_value = ([""] * len(discovery_result.ATTRS),)
            dp_columns = discovery_result.ATTRS
            dp = iter(discovery_result)
            r[-1].extend(dp_columns)
        for (mo_id, name, address, is_managed,
             sa_profile, o_profile, auth_profile, ad, m_segment,
             vendor, platform, version, tags
             ) in mos.values_list(
                "id", "name", "address", "is_managed",
                "profile", "object_profile__name", "auth_profile__name",
                "administrative_domain__name", "segment",
                "vendor", "platform", "version", "tags").order_by("id"):
            if (mos_filter and mo_id not in mos_filter) or not mos_id:
                continue
            mo_continer = next(container_lookup)
            r += [translate_row(row([
                mo_id,
                name,
                address,
                next(hn)[0],
                "managed" if is_managed else "unmanaged",
                Profile.get_by_id(sa_profile),
                o_profile,
                Vendor.get_by_id(vendor) if vendor else "",
                Platform.get_by_id(platform) if platform else "",
                Firmware.get_by_id(version) if version else "",
                # Serial
                mo_continer[0].get("serial", ""),
                auth_profile,
                _("Yes") if avail.get(mo_id, None) else _("No"),
                ad,
                mo_continer[0].get("text", ""),
                NetworkSegment.get_by_id(m_segment) if m_segment else "",
                next(iface_count)[0],
                next(link_count)[0],
                next(rc)[0]
            ]), cmap)]
            if "adm_path" in columns.split(","):
                r[-1].extend([ad] + list(ad_path[ad]))
            if "interface_type_count" in columns.split(","):
                r[-1].extend(next(iss)[0])
            if "object_caps" in columns.split(","):
                r[-1].extend(next(ccc)[0])
            if "object_tags" in columns.split(","):
                r[-1].append(",".join(tags if tags else []))
            if "sorted_tags" in columns.split(","):
                out_tags = [""] * len(tags_o)
                try:
                    if tags:
                        for m in tags:
                            out_tags[tags_o.index(m)] = m
                except ValueError:
                    logger.warning("Bad value for tag: %s", m)
                r[-1].extend(out_tags)
            if "discovery_problem" in columns.split(","):
                r[-1].extend(next(dp)[0])

        filename = "mo_detail_report_%s" % datetime.datetime.now().strftime("%Y%m%d")
        if o_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response[
                "Content-Disposition"] = "attachment; filename=\"%s.csv\"" % filename
            writer = csv.writer(response, dialect='excel', delimiter=';')
            writer.writerows(r)
            return response
        elif o_format == "xlsx":
            # with tempfile.NamedTemporaryFile(mode="wb") as f:

            #    wb = xlsxwriter.Workbook(f.name)
                response = StringIO.StringIO()
                wb = xlsxwriter.Workbook(response)
                ws = wb.add_worksheet("Objects")
                for rn, x in enumerate(r):
                    for cn, c in enumerate(x):
                        ws.write(rn, cn, c)
                ws.autofilter(0, 0, rn, cn)
                wb.close()
                response.seek(0)
                response = HttpResponse(response.getvalue(),
                                        content_type="application/vnd.ms-excel")
                # response = HttpResponse(
                #     content_type="application/x-ms-excel")
                response[
                    "Content-Disposition"] = "attachment; filename=\"%s.xlsx\"" % filename
                response.close()
                return response
