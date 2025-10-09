# ---------------------------------------------------------------------
# fm.reportobjectdetail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import datetime
import csv
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import TemporaryFile

# Third-party modules
from django.http import HttpResponse
from pymongo import ReadPreference
import xlsxwriter

# NOC modules
from noc.core.mongo.connection import get_db
from noc.services.web.base.extapplication import ExtApplication, view
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import StringParameter, BooleanParameter
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.platform import Platform
from noc.core.comp import smart_text

logger = logging.getLogger(__name__)


def get_column_width(name):
    excel_column_format = {
        "ID": 6,
        "OBJECT1_NAME": 38,
        "OBJECT2_NAME": 38,
        "OBJECT_STATUS": 10,
        "OBJECT_PROFILE": 17,
        "OBJECT_PLATFORM": 25,
        "AVAIL": 6,
        "ADMIN_DOMAIN": 25,
        "PHYS_INTERFACE_COUNT": 5,
    }
    if name.startswith("Up") or name.startswith("Down") or name.startswith("-"):
        return 8
    if name.startswith("ADM_PATH"):
        return excel_column_format["ADMIN_DOMAIN"]
    if name in excel_column_format:
        return excel_column_format[name]
    return 15


class ReportLinksDetail(object):
    """Report for MO links detail"""

    def __init__(self, mo_ids):
        self.mo_ids = mo_ids
        self.out = self.load(mo_ids)

    @staticmethod
    def load(mo_ids):
        # match = {"links.mo": {"$in": mo_ids}}
        match = {"int.managed_object": {"$in": mo_ids}}
        group = {
            "_id": "$_id",
            "links": {
                "$push": {
                    "iface_n": "$int.name",
                    "iface_id": "$int._id",
                    "iface_descr": "$int.description",
                    "iface_speed": "$int.in_speed",
                    "dis_method": "$discovery_method",
                    "last_seen": "$last_seen",
                    "mo": "$int.managed_object",
                }
            },
        }
        value = (
            get_db()["noc.links"]
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(
                [
                    {"$unwind": "$interfaces"},
                    {
                        "$lookup": {
                            "from": "noc.interfaces",
                            "localField": "interfaces",
                            "foreignField": "_id",
                            "as": "int",
                        }
                    },
                    {"$match": match},
                    {"$group": group},
                ],
                allowDiskUse=True,
            )
        )

        return {v["_id"]: v["links"] for v in value if v["_id"]}

    def __getitem__(self, item):
        return self.out.get(item, [])


class ReportLinkDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Link Detail")
    title = _("Link Detail")

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    @view(
        "^download/$",
        method=["GET"],
        access="launch",
        api=True,
        validate={
            "administrative_domain": StringParameter(required=False),
            "pool": StringParameter(required=False),
            "segment": StringParameter(required=False),
            "resource_group": StringParameter(required=False),
            "ids": StringParameter(required=False),
            "is_managed": BooleanParameter(required=False),
            "avail_status": BooleanParameter(required=False),
            "columns": StringParameter(required=False),
            "o_format": StringParameter(choices=["csv", "csv_zip", "xlsx"]),
        },
    )
    def api_report(
        self,
        request,
        o_format,
        is_managed=None,
        administrative_domain=None,
        resource_group=None,
        pool=None,
        segment=None,
        avail_status=False,
        columns=None,
        ids=None,
        enable_autowidth=False,
    ):
        def row(row):
            def qe(v):
                if v is None:
                    return ""
                if isinstance(v, str):
                    return smart_text(v)
                if isinstance(v, datetime.datetime):
                    return v.strftime("%Y-%m-%d %H:%M:%S")
                if not isinstance(v, str):
                    return str(v)
                return v

            return [qe(x) for x in row]

        def translate_row(row, cmap):
            return [row[i] for i in cmap]

        type_columns = ["Up/10G", "Up/1G", "Up/100M", "Down/-", "-"]

        cols = [
            "object1_admin_domain",
            # "id",
            "object1_name",
            "object1_address",
            "object1_platform",
            "object1_segment",
            "object1_tags",
            "object1_iface",
            "object1_descr",
            "object1_speed",
            "object2_admin_domain",
            "object2_name",
            "object2_address",
            "object2_platform",
            "object2_segment",
            "object2_tags",
            "object2_iface",
            "object2_descr",
            "object2_speed",
            "link_proto",
            "last_seen",
        ]

        header_row = [
            "OBJECT1_ADMIN_DOMAIN",
            "OBJECT1_NAME",
            "OBJECT1_ADDRESS",
            "OBJECT1_PLATFORM",
            "OBJECT1_SEGMENT",
            "OBJECT1_TAGS",
            "OBJECT1_IFACE",
            "OBJECT1_DESCR",
            "OBJECT1_SPEED",
            "OBJECT2_ADMIN_DOMAIN",
            "OBJECT2_NAME",
            "OBJECT2_ADDRESS",
            "OBJECT2_PLATFORM",
            "OBJECT2_SEGMENT",
            "OBJECT2_TAGS",
            "OBJECT2_IFACE",
            "OBJECT2_DESCR",
            "OBJECT2_SPEED",
            "LINK_PROTO",
            "LAST_SEEN",
        ]

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
        # self.logger.info(r)
        # self.logger.info("---------------------------------")
        # print("-----------%s------------%s" % (administrative_domain, columns))

        pool = Pool.get_by_name(pool)
        mos = ManagedObject.objects.filter()
        if ids:
            mos = ManagedObject.objects.filter(id__in=[ids])
        if is_managed is not None:
            mos = ManagedObject.objects.filter(is_managed=is_managed)
        if pool:
            mos = mos.filter(pool=pool)
        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        if administrative_domain:
            ads = AdministrativeDomain.get_nested_ids(int(administrative_domain))
            mos = mos.filter(administrative_domain__in=ads)
        if resource_group:
            resource_group = ResourceGroup.get_by_id(resource_group)
            mos = mos.filter(
                effective_service_groups__overlap=ResourceGroup.get_nested_ids(resource_group)
            )
        if segment:
            segment = NetworkSegment.objects.filter(id=segment).first()
            if segment:
                mos = mos.filter(segment__in=segment.get_nested_ids())
        mos_id = list(mos.values_list("id", flat=True))

        rld = ReportLinksDetail(mos_id)
        mo_resolv = {
            mo[0]: mo[1:]
            for mo in ManagedObject.objects.filter().values_list(
                "id",
                "administrative_domain__name",
                "name",
                "address",
                "segment",
                "platform",
                "labels",
            )
        }

        for link in rld.out:
            if len(rld.out[link]) != 2:
                # Multilink or bad link
                continue
            s1, s2 = rld.out[link]
            seg1, seg2 = None, None
            if "object1_segment" in columns.split(",") or "object2_segment" in columns.split(","):
                seg1, seg2 = mo_resolv[s1["mo"][0]][3], mo_resolv[s2["mo"][0]][3]
            plat1, plat2 = None, None
            if "object1_platform" in columns.split(",") or "object2_platform" in columns.split(","):
                plat1, plat2 = mo_resolv[s1["mo"][0]][4], mo_resolv[s2["mo"][0]][4]
            r += [
                translate_row(
                    row(
                        [
                            mo_resolv[s1["mo"][0]][0],
                            mo_resolv[s1["mo"][0]][1],
                            mo_resolv[s1["mo"][0]][2],
                            "" if not plat1 else Platform.get_by_id(plat1),
                            "" if not seg1 else NetworkSegment.get_by_id(seg1),
                            ";".join(mo_resolv[s1["mo"][0]][5] or []),
                            s1["iface_n"][0],
                            s1.get("iface_descr")[0] if s1.get("iface_descr") else "",
                            s1.get("iface_speed")[0] if s1.get("iface_speed") else 0,
                            mo_resolv[s2["mo"][0]][0],
                            mo_resolv[s2["mo"][0]][1],
                            mo_resolv[s2["mo"][0]][2],
                            "" if not plat2 else Platform.get_by_id(plat2),
                            "" if not seg2 else NetworkSegment.get_by_id(seg2),
                            ";".join(mo_resolv[s2["mo"][0]][5] or []),
                            s2["iface_n"][0],
                            s2.get("iface_descr")[0] if s2.get("iface_descr") else "",
                            s2.get("iface_speed")[0] if s2.get("iface_speed") else 0,
                            s2.get("dis_method", ""),
                            s2.get("last_seen", ""),
                        ]
                    ),
                    cmap,
                )
            ]
        filename = "links_detail_report_%s" % datetime.datetime.now().strftime("%Y%m%d")
        if o_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="%s.csv"' % filename
            writer = csv.writer(response, dialect="excel", delimiter=",", quoting=csv.QUOTE_MINIMAL)
            writer.writerows(r)
            return response
        if o_format == "csv_zip":
            response = BytesIO()
            f = TextIOWrapper(TemporaryFile(mode="w+b"), encoding="utf-8")
            writer = csv.writer(f, dialect="excel", delimiter=";", quotechar='"')
            writer.writerows(r)
            f.seek(0)
            with ZipFile(response, "w", compression=ZIP_DEFLATED) as zf:
                zf.writestr("%s.csv" % filename, f.read())
                zf.filename = "%s.csv.zip" % filename
            # response = HttpResponse(content_type="text/csv")
            response.seek(0)
            response = HttpResponse(response.getvalue(), content_type="application/zip")
            response["Content-Disposition"] = 'attachment; filename="%s.csv.zip"' % filename
            return response
        if o_format == "xlsx":
            response = BytesIO()
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
