# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.reportobjectdetail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import datetime
import csv

# Third-party modules
import six
from six import StringIO
import xlsxwriter
from django.http import HttpResponse

# NOC modules
from noc.main.models.pool import Pool
from noc.lib.app.extapplication import ExtApplication, view
from noc.lib.app.reportdatasources.base import ReportModelFilter
from noc.lib.app.reportdatasources.report_objectlinkcount import ReportObjectLinkCount
from noc.lib.app.reportdatasources.report_objectifacestypestat import ReportObjectIfacesTypeStat
from noc.lib.app.reportdatasources.report_container import ReportContainer, ReportContainerData
from noc.lib.app.reportdatasources.report_discoveryresult import ReportDiscoveryResult
from noc.lib.app.reportdatasources.report_objectifacesstatusstat import ReportObjectIfacesStatusStat
from noc.lib.app.reportdatasources.report_objectcaps import ReportObjectCaps
from noc.lib.app.reportdatasources.report_objecthostname import ReportObjectsHostname1
from noc.lib.app.reportdatasources.report_objectconfig import ReportObjectConfig
from noc.lib.app.reportdatasources.report_objectattributes import ReportObjectAttributes
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


def get_column_width(name):
    excel_column_format = {
        "ID": 6,
        "OBJECT_NAME": 38,
        "OBJECT_STATUS": 10,
        "OBJECT_PROFILE": 17,
        "OBJECT_PLATFORM": 25,
        "AVAIL": 6,
        "ADMIN_DOMAIN": 25,
        "PHYS_INTERFACE_COUNT": 5,
    }
    if name.startswith("Up") or name.startswith("Down") or name.startswith("-"):
        return 8
    elif name.startswith("ADM_PATH"):
        return excel_column_format["ADMIN_DOMAIN"]
    elif name in excel_column_format:
        return excel_column_format[name]
    return 15


class ReportAdPath(object):
    """
    Return AD path
    """

    def __init__(self):
        self.out = self.load()

    def load(self):
        from django.db import connection

        cursor = connection.cursor()
        cursor.execute(
            """SELECT ad.id, ad.name, r.name, ad2.name
                          FROM sa_administrativedomain r
                          JOIN sa_administrativedomain ad ON ad.parent_id = r.id
                          JOIN sa_administrativedomain ad2 ON r.parent_id = ad2.id;
                """
        )
        return {r[1]: (r[2], r[3]) for r in cursor}

    def __getitem__(self, item):
        return self.out.get(item, [])


class ReportObjectDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Object Detail")
    title = _("Object Detail")

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    def get_report_object(
        self, user=None, is_managed=None, adm=None, selector=None, pool=None, segment=None, ids=None
    ):
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

    @view(
        "^download/$",
        method=["GET"],
        access="launch",
        api=True,
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
            "o_format": StringParameter(choices=["csv", "xlsx"]),
        },
    )
    def api_report(
        self,
        request,
        o_format,
        is_managed=None,
        administrative_domain=None,
        selector=None,
        pool=None,
        segment=None,
        avail_status=False,
        columns=None,
        ids=None,
        detail_stat=None,
        enable_autowidth=False,
    ):
        def row(row):
            def qe(v):
                if v is None:
                    return ""
                if isinstance(v, six.text_type):
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

        type_columns = ["Up/10G", "Up/1G", "Up/100M", "Up/10M", "Down/-", "-"]
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
            "object_attr_hwversion",
            "object_version",
            "object_attr_bootprom",
            "object_serial",
            "object_attr_patch",
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
            "OBJECT_HWVERSION",
            "OBJECT_VERSION",
            "OBJECT_BOOTPROM",
            "OBJECT_SERIAL",
            "OBJECT_ATTR_PATCH",
            "AUTH_PROFILE",
            "AVAIL",
            "ADMIN_DOMAIN",
            "CONTAINER",
            "SEGMENT",
            "PHYS_INTERFACE_COUNT",
            "LINK_COUNT",
            "LAST_CONFIG_TS",
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
        mos = self.get_report_object(
            request.user, is_managed, administrative_domain, selector, pool, segment, ids
        )
        columns_filter = set(columns.split(","))
        mos_id = tuple(mos.order_by("id").values_list("id", flat=True))
        mos_filter = None
        if detail_stat:
            ref = ReportModelFilter()
            ids = list(six.itervalues(ref.proccessed(detail_stat)))
            mos_filter = set(mos_id).intersection(ids[0])
            mos_id = sorted(mos_filter)
        avail = {}
        if "avail" in columns_filter:
            avail = ObjectStatus.get_statuses(mos_id)
        link_count = iter(ReportObjectLinkCount(mos_id))
        iface_count = iter(ReportObjectIfacesTypeStat(mos_id))
        if "container" in columns_filter:
            container_lookup = iter(ReportContainerData(mos_id))
        else:
            container_lookup = None
        if "object_serial" in columns_filter:
            container_serials = iter(ReportContainer(mos_id))
        else:
            container_serials = None
        if "interface_type_count" in columns_filter:
            iss = iter(ReportObjectIfacesStatusStat(mos_id))
        else:
            iss = None
        if "object_attr_patch" in columns_filter or "object_serial" in columns_filter:
            roa = iter(ReportObjectAttributes(mos_id))
        else:
            roa = None
        hn = iter(ReportObjectsHostname1(mos_id))
        rc = iter(ReportObjectConfig(mos_id))
        # ccc = iter(ReportObjectCaps(mos_id))
        if "adm_path" in columns_filter:
            ad_path = ReportAdPath()
            r[-1].extend([_("ADM_PATH1"), _("ADM_PATH1"), _("ADM_PATH1")])
        if "interface_type_count" in columns_filter:
            r[-1].extend(type_columns)
        if "object_caps" in columns_filter:
            object_caps = ReportObjectCaps(mos_id)
            caps_columns = list(six.itervalues(object_caps.ATTRS))
            ccc = iter(object_caps)
            r[-1].extend(caps_columns)
        if "object_tags" in columns_filter:
            r[-1].extend([_("OBJECT_TAGS")])
        if "sorted_tags" in columns_filter:
            tags = set()
            for s in (
                ManagedObject.objects.filter()
                .exclude(tags=None)
                .values_list("tags", flat=True)
                .distinct()
            ):
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
        for (
            mo_id,
            name,
            address,
            is_managed,
            sa_profile,
            o_profile,
            auth_profile,
            ad,
            m_segment,
            vendor,
            platform,
            version,
            tags,
        ) in (
            mos.values_list(
                "id",
                "name",
                "address",
                "is_managed",
                "profile",
                "object_profile__name",
                "auth_profile__name",
                "administrative_domain__name",
                "segment",
                "vendor",
                "platform",
                "version",
                "tags",
            )
            .order_by("id")
            .iterator()
        ):
            if (mos_filter and mo_id not in mos_filter) or not mos_id:
                continue
            if container_serials:
                mo_serials = next(container_serials)
            else:
                mo_serials = [{}]
            if container_lookup:
                mo_continer = next(container_lookup)
            else:
                mo_continer = ("",)
            if roa:
                serial, hw_ver, boot_prom, patch = next(roa)[0]  # noqa
            else:
                serial, hw_ver, boot_prom, patch = "", "", "", ""  # noqa
            r.append(
                translate_row(
                    row(
                        [
                            mo_id,
                            name,
                            address,
                            next(hn)[0],
                            "managed" if is_managed else "unmanaged",
                            Profile.get_by_id(sa_profile),
                            o_profile,
                            Vendor.get_by_id(vendor) if vendor else "",
                            Platform.get_by_id(platform) if platform else "",
                            hw_ver,
                            Firmware.get_by_id(version) if version else "",
                            boot_prom,
                            # Serial
                            mo_serials[0].get("serial", "") or serial,
                            patch or "",
                            auth_profile,
                            _("Yes") if avail.get(mo_id, None) else _("No"),
                            ad,
                            mo_continer[0],
                            NetworkSegment.get_by_id(m_segment) if m_segment else "",
                            next(iface_count)[0],
                            next(link_count)[0],
                            next(rc)[0],
                        ]
                    ),
                    cmap,
                )
            )
            if "adm_path" in columns_filter:
                r[-1].extend([ad] + list(ad_path[ad]))
            if "interface_type_count" in columns_filter:
                r[-1].extend(next(iss)[0])
            if "object_caps" in columns_filter:
                r[-1].extend(next(ccc)[0])
            if "object_tags" in columns_filter:
                r[-1].append(",".join(tags if tags else []))
            if "sorted_tags" in columns_filter:
                out_tags = [""] * len(tags_o)
                try:
                    if tags:
                        for m in tags:
                            out_tags[tags_o.index(m)] = m
                except ValueError:
                    logger.warning("Bad value for tag: %s", m)
                r[-1].extend(out_tags)
            if "discovery_problem" in columns_filter:
                r[-1].extend(next(dp)[0])
        filename = "mo_detail_report_%s" % datetime.datetime.now().strftime("%Y%m%d")
        if o_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="%s.csv"' % filename
            writer = csv.writer(response, dialect="excel", delimiter=";", quotechar='"')
            writer.writerows(r)
            return response
        elif o_format == "xlsx":
            response = StringIO()
            wb = xlsxwriter.Workbook(response)
            cf1 = wb.add_format({"bottom": 1, "left": 1, "right": 1, "top": 1})
            ws = wb.add_worksheet("Objects")
            max_column_data_length = {}
            for rn, x in enumerate(r):
                for cn, c in enumerate(x):
                    if rn and (
                        r[0][cn] not in max_column_data_length
                        or len(str(c)) > max_column_data_length[r[0][cn]]
                    ):
                        max_column_data_length[r[0][cn]] = len(str(c))
                    ws.write(rn, cn, c, cf1)
            # for
            ws.autofilter(0, 0, rn, cn)
            ws.freeze_panes(1, 0)
            for cn, c in enumerate(r[0]):
                # Set column width
                width = get_column_width(c)
                if enable_autowidth and width < max_column_data_length[c]:
                    width = max_column_data_length[c]
                ws.set_column(cn, cn, width=width)
            wb.close()
            response.seek(0)
            response = HttpResponse(response.getvalue(), content_type="application/vnd.ms-excel")
            # response = HttpResponse(
            #     content_type="application/x-ms-excel")
            response["Content-Disposition"] = 'attachment; filename="%s.xlsx"' % filename
            response.close()
            return response
