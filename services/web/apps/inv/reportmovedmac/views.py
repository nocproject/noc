# ---------------------------------------------------------------------
# fm.reportmovedmac application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import datetime
import csv
import ast
import re
import bisect
from operator import itemgetter
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import TemporaryFile

# Third-party modules
import xlsxwriter
from django.http import HttpResponse

# NOC modules
from noc.core.clickhouse.connect import connection
from noc.core.mac import MAC
from noc.main.models.pool import Pool
from noc.services.web.base.extapplication import ExtApplication, view
from noc.sa.interfaces.base import StringParameter, BooleanParameter
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.useraccess import UserAccess
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.macvendor import MACVendor
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.core.translation import ugettext as _
from noc.config import config

logger = logging.getLogger(__name__)

MULTICAST_MACS = [
    ("01:00:5E:00:00:00", "01:00:5E:FF:FF:FF"),
    ("01:80:C2:00:00:00", "01:80:C2:FF:FF:FF"),
]


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
    if name.startswith("ADM_PATH"):
        return excel_column_format["ADMIN_DOMAIN"]
    if name in excel_column_format:
        return excel_column_format[name]
    return 15


"""
Find mac, that more 1 unique interface the requested time range groupUniqArray has high
 memory consumption (that groupUniqArray), so used subquery for filter data.
"""
MAC_MOVED_QUERY = f"""
SELECT
   managed_object,
   smac,
   dictGetString('{config.clickhouse.db_dictionaries}.managedobject', 'name', managed_object),
   dictGetString('{config.clickhouse.db_dictionaries}.managedobject', 'address', managed_object),
   dictGetString('{config.clickhouse.db_dictionaries}.managedobject', 'administrative_domain', managed_object),
   arrayReduce('groupUniqArray', ifaces),
   arrayReduce('groupUniqArray', migrate_ifaces),
   iface_count
FROM (
  SELECT
     managed_object,
     MACNumToString(mac) as smac,
     groupArray((interface, toUnixTimestamp(ts))) as ifaces,
     groupArray(interface) as migrate_ifaces,
     uniq(interface) as iface_count
     FROM mac
     WHERE %%s and %s and date >= '%%s' and date < '%%s'
     GROUP BY mac, managed_object, vlan
     HAVING iface_count > 1
)
    """ % " AND ".join(
    "(mac < %s or mac > %s)" % (int(MAC(x[0])), int(MAC(x[1]))) for x in MULTICAST_MACS
)

DEVICE_MOVED_QUERY = """SELECT
   managed_object, groupArray((ts, serials)) as serial_arr
   FROM managedobjects
   WHERE date = '%s' or date = '%s'
   GROUP BY managed_object HAVING uniq(arraySort(serials)) > 1 ORDER BY managed_object
"""


def get_interface(ifaces: str):
    r = sorted(ast.literal_eval(ifaces), key=itemgetter(1))
    iface_from, iface_to = r[0][0], r[-1][0]
    if iface_from == iface_to:
        iface_from, iface_to = (
            r[bisect.bisect_left(r, (r[-1][0], 0)) - 1][0],
            r[-1][0],
        )
    # iface_from, iface_to = ast.literal_eval(migrate_ifaces)
    return iface_from, iface_to, r[bisect.bisect_left(r, (iface_to, 0))]


rx_port_num = re.compile(r"\d+$")


class ReportMovedMacApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Moved MACs")
    title = _("Moved MACs")

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    def get_report_object(
        self, user=None, is_managed=None, adm=None, resource_group=None, pool=None, segment=None
    ):
        mos = ManagedObject.objects.filter()
        if user.is_superuser and not adm and not resource_group and not segment:
            mos = ManagedObject.objects.filter()
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
        if resource_group:
            resource_group = ResourceGroup.get_by_id(resource_group)
            mos = mos.filter(
                effective_service_groups__overlap=ResourceGroup.get_nested_ids(resource_group)
            )
        if segment:
            segment = NetworkSegment.objects.filter(id=segment).first()
            if segment:
                mos = mos.filter(segment__in=segment.get_nested_ids())
        return mos

    @view(
        r"^download/$",
        method=["GET"],
        access="launch",
        api=True,
        validate={
            "from_date": StringParameter(required=True),
            "to_date": StringParameter(required=True),
            "administrative_domain": StringParameter(required=False),
            # "pool": StringParameter(required=False),
            "segment": StringParameter(required=False),
            "resource_group": StringParameter(required=False),
            "interface_profile": StringParameter(required=False),
            "exclude_serial_change": BooleanParameter(default=False),
            "columns": StringParameter(required=False),
            "o_format": StringParameter(choices=["csv", "csv_zip", "xlsx"]),
        },
    )
    def api_report(
        self,
        request,
        reporttype=None,
        from_date=None,
        to_date=None,
        object_profile=None,
        filter_default=None,
        exclude_zero=None,
        interface_profile=None,
        resource_group=None,
        administrative_domain=None,
        columns=None,
        o_format=None,
        enable_autowidth=False,
        exclude_serial_change=False,
        **kwargs,
    ):
        def translate_row(row, cmap):
            return [row[i] for i in cmap]

        cols = [
            "object_name",
            "object_address",
            "object_adm_domain",
            "event_type",
            "sn_changed",
            "vendor_mac",
            "mac",
            "migrate_ts",
            "from_iface_name",
            "from_iface_down",
            "to_iface_name",
            "to_iface_down",
        ]

        header_row = [
            "OBJECT_NAME",
            "OBJECT_ADDRESS",
            "OBJECT_ADM_DOMAIN",
            "EVENT_TYPE",
            "SN_CHANGED",
            "VENDOR_MAC",
            "MAC",
            "MIGRATE_TS",
            "FROM_IFACE_NAME",
            "FROM_IFACE_DOWN",
            "TO_IFACE_NAME",
            "TO_IFACE_DOWN",
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

        # Date Time Block
        if not from_date:
            from_date = datetime.datetime.now() - datetime.timedelta(days=1)
        else:
            from_date = datetime.datetime.strptime(from_date, "%d.%m.%Y")
        if not to_date or from_date == to_date:
            to_date = from_date + datetime.timedelta(days=1)
        else:
            to_date = datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)
        # interval = (to_date - from_date).days
        # ts_from_date = time.mktime(from_date.timetuple())
        # ts_to_date = time.mktime(to_date.timetuple())

        mos = self.get_report_object(
            user=request.user, adm=administrative_domain, resource_group=resource_group
        )
        mos_id = set(mos.order_by("bi_id").values_list("bi_id", flat=True))
        if interface_profile:
            interface_profile = InterfaceProfile.objects.get(id=interface_profile)
            iface_filter = f"dictGetString('{config.clickhouse.db_dictionaries}.interfaceattributes', 'profile', (managed_object, interface)) == '{interface_profile.name}'"
        else:
            iface_filter = "is_uni = 1"
        serials_changed = {}
        ch = connection()
        for row in ch.execute(
            DEVICE_MOVED_QUERY
            % (
                from_date.date().isoformat(),
                (to_date.date() - datetime.timedelta(days=1)).isoformat(),
            )
        ):
            serials_changed[int(row[0])] = row[1]
        for (
            mo,
            mac,
            mo_name,
            mo_address,
            mo_adm_domain,
            ifaces,
            migrate_ifaces,
            migrate_count,
        ) in ch.execute(
            MAC_MOVED_QUERY
            % (iface_filter, from_date.date().isoformat(), to_date.date().isoformat())
        ):
            if int(mo) not in mos_id:
                continue
            if exclude_serial_change and int(mo) in serials_changed:
                continue
            iface_from, iface_to, migrate = get_interface(ifaces)
            event_type = _("Migrate")
            if (
                rx_port_num.search(iface_from).group() == rx_port_num.search(iface_to).group()
                and iface_from != iface_to
            ):
                event_type = _("Migrate (Device Changed)")
            r += [
                translate_row(
                    [
                        mo_name,
                        mo_address,
                        mo_adm_domain,
                        event_type,
                        _("Yes") if int(mo) in serials_changed else _("No"),
                        MACVendor.get_vendor(mac),
                        mac,
                        datetime.datetime.fromtimestamp(migrate[1]).isoformat(sep=" "),  # TS
                        iface_from,
                        "--",
                        iface_to,
                        "--",
                    ],
                    cmap,
                )
            ]

        filename = "macs_move_report_%s" % datetime.datetime.now().strftime("%Y%m%d")
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
            ws = wb.add_worksheet("Alarms")
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
            response["Content-Disposition"] = 'attachment; filename="%s.xlsx"' % filename
            response.close()
            return response
