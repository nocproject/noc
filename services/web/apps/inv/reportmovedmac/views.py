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
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import TemporaryFile

# Third-party modules
import xlsxwriter
from django.http import HttpResponse

# NOC modules
from noc.core.clickhouse.connect import connection
from noc.main.models.pool import Pool
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.interfaces.base import StringParameter
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.useraccess import UserAccess
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.macvendor import MACVendor
from noc.inv.models.interfaceprofile import InterfaceProfile
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


MAC_MOVED_QUERY = """SELECT
   managed_object,
   MACNumToString(mac) as smac,
   dictGetString('managedobject', 'name', managed_object),
   dictGetString('managedobject', 'address', managed_object),
   dictGetString('managedobject', 'adm_domain_name', managed_object),
   arrayStringConcat(groupUniqArray(interface), ';') as ifaces
   FROM mac
   WHERE %s and date >= '%s' and date < '%s' group by mac, managed_object having uniqExact(interface) > 1
    """


class ReportMovedMacApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Moved Mac")
    title = _("Moved Mac")

    SEGMENT_PATH_DEPTH = 7
    CONTAINER_PATH_DEPTH = 7

    def get_report_object(
        self, user=None, is_managed=None, adm=None, selector=None, pool=None, segment=None
    ):
        mos = ManagedObject.objects.filter()
        if user.is_superuser and not adm and not selector and not segment:
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
        if selector:
            selector = ManagedObjectSelector.get_by_id(int(selector))
            mos = mos.filter(selector.Q)
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
            "selector": StringParameter(required=False),
            "interface_profile": StringParameter(required=False),
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
        selector=None,
        administrative_domain=None,
        columns=None,
        o_format=None,
        enable_autowidth=False,
        **kwargs,
    ):
        def translate_row(row, cmap):
            return [row[i] for i in cmap]

        cols = [
            "vendor_mac",
            "mac",
            "object_name",
            "object_address",
            "object_adm_domain",
            "ifaces",
            # "iface_description",
        ]

        header_row = [
            "VENDOR_MAC",
            "MAC",
            "OBJECT_NAME",
            "OBJECT_ADDRESS",
            "OBJECT_ADM_DOMAIN",
            "IFACE_NAME",
            # "IFACE_DESCRIPTION",
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
            user=request.user, adm=administrative_domain, selector=selector
        )
        mos_id = set(mos.order_by("bi_id").values_list("bi_id", flat=True))
        if interface_profile:
            interface_profile = InterfaceProfile.objects.get(id=interface_profile)
            iface_filter = (
                "dictGetString('interfaceattributes', 'profile', (managed_object, interface)) == '%s'"
                % interface_profile.name
            )
        else:
            iface_filter = "is_uni = 1"

        ch = connection()
        for mo, mac, mo_name, mo_address, mo_adm_domain, ifaces in ch.execute(
            MAC_MOVED_QUERY
            % (iface_filter, from_date.date().isoformat(), to_date.date().isoformat())
        ):
            if int(mo) not in mos_id:
                continue
            r += [
                translate_row(
                    [
                        MACVendor.get_vendor(mac),
                        mac,
                        mo_name,
                        mo_address,
                        mo_adm_domain,
                        ifaces,
                        "",
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
        elif o_format == "csv_zip":
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
        elif o_format == "xlsx":
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
