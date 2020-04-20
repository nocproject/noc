# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.reportmaxmetrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from collections import defaultdict, Iterable
from collections import namedtuple
import csv
from io import BytesIO

# Third-party modules
import xlsxwriter
from django.http import HttpResponse

# NOC modules
from noc.inv.models.platform import Platform
from noc.inv.models.networksegment import NetworkSegment
from noc.core.clickhouse.connect import connection as ch_connection
from noc.core.clickhouse.error import ClickhouseError
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.link import Link
from noc.sa.models.managedobject import ManagedObject
from noc.lib.app.reportdatasources.report_container import ReportContainerData
from noc.sa.models.useraccess import UserAccess
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.interfaces.base import StringParameter, BooleanParameter
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.core.translation import ugettext as _


def get_column_width(name):
    excel_column_format = {
        "ID": 6,
        "OBJECT_NAME": 38,
        "OBJECT_STATUS": 10,
        "OBJECT_PROFILE": 17,
        "OBJECT_PLATFORM": 25,
        "AVAIL": 6,
        "OBJECT_ADM_DOMAIN": 25,
        "PHYS_INTERFACE_COUNT": 5,
    }
    if name.startswith("Up") or name.startswith("Down") or name.startswith("-"):
        return 8
    elif name.startswith("ADM_PATH"):
        return excel_column_format["ADMIN_DOMAIN"]
    elif name in excel_column_format:
        return excel_column_format[name]
    return 15


class ReportMaxMetricsmaxDetailApplication(ExtApplication):
    menu = _("Reports") + "|" + _("Load Metrics max")
    title = _("Load Metrics max")

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
            "object_profile": StringParameter(required=False),
            "interface_profile": StringParameter(required=False),
            "exclude_zero": BooleanParameter(required=False),
            "filter_default": BooleanParameter(required=False),
            "columns": StringParameter(required=False),
            "description": StringParameter(required=False),
            "o_format": StringParameter(choices=["csv", "xlsx"]),
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
        exclude_zero=True,
        interface_profile=None,
        selector=None,
        administrative_domain=None,
        columns=None,
        description=None,
        o_format=None,
        enable_autowidth=False,
        **kwargs
    ):
        # get maximum metrics for the period
        def get_interface_metrics(managed_objects, from_date, to_date):
            if not isinstance(managed_objects, Iterable):
                managed_objects = [managed_objects]
            bi_map = {str(getattr(mo, "bi_id", mo)): mo for mo in managed_objects}

            from_date = from_date.replace(microsecond=0)
            to_date = to_date.replace(microsecond=0)
            SQL = """SELECT managed_object, path[4] as iface,
                             dictGetString('interfaceattributes','description' , (managed_object, arrayStringConcat(path))) AS iface_description,
                             dictGetString('interfaceattributes', 'profile', (managed_object, arrayStringConcat(path))) as profile,
                             dictGetUInt64('interfaceattributes','in_speed' , (managed_object, arrayStringConcat(path))) AS iface_speed, divide(max(load_in),1048576) as load_in_max,
                             divide(max(load_out),1048576) as load_out_max, argMax(ts,load_in) as max_load_in_time,
                             argMax(ts,load_out) as max_load_out_time, divide(avg(load_in),1048576) as avg_load_in,
                             divide(avg(load_out),1048576) as avg_load_out
                    FROM interface
                    WHERE
                      ts >= toDateTime('%s')
                      AND ts <= toDateTime('%s')
                      AND managed_object IN (%s)
                    GROUP BY managed_object, path
                    """ % (
                # from_date.date().isoformat(),
                # to_date.date().isoformat(),
                from_date.isoformat(sep=" "),
                to_date.isoformat(sep=" "),
                ", ".join(bi_map),
            )
            ch = ch_connection()
            metric_map = defaultdict(dict)
            try:
                for (
                    mo_bi_id,
                    iface,
                    iface_description,
                    profile,
                    iface_speed,
                    load_in_max,
                    load_out_max,
                    max_load_in_time,
                    max_load_out_time,
                    avg_load_in,
                    avg_load_out,
                ) in ch.execute(post=SQL):
                    mo = bi_map.get(mo_bi_id)
                    if mo:
                        metric_map[mo][iface] = {
                            "max_load_in": float(load_in_max),
                            "max_load_out": float(load_out_max),
                            "max_load_in_time": max_load_in_time,
                            "max_load_out_time": max_load_out_time,
                            "avg_load_in": float(avg_load_in),
                            "avg_load_out": float(avg_load_out),
                            "description": iface_description,
                            "profile": profile,
                            "bandwidth": iface_speed,
                        }
            except ClickhouseError:
                pass
            return metric_map

        def translate_row(row, cmap):
            return [row[i] for i in cmap]

        cols = [
            "id",
            "object_name",
            "object_address",
            "object_platform",
            "object_adm_domain",
            "object_segment",
            "object_container",
            # "object_hostname",
            # "object_status",
            # "profile_name",
            # "object_profile",
            # "object_vendor",
            "iface_name",
            "iface_description",
            "iface_speed",
            "max_load_in",
            "max_load_in_time",
            "max_load_out",
            "max_load_out_time",
            "avg_load_in",
            "avg_load_out",
            "uplink_iface_name",
            "uplink_iface_description",
            "uplink_max_load_in",
            "uplink_max_load_in_time",
            "uplink_max_load_out",
            "uplink_max_load_out_time",
            "uplink_avg_load_in",
            "uplink_avg_load_out",
            "uplink_iface_speed",
        ]

        header_row = [
            "ID",
            _("OBJECT_NAME"),
            _("OBJECT_ADDRESS"),
            _("OBJECT_PLATFORM"),
            _("OBJECT_ADMDOMAIN"),
            _("OBJECT_SEGMENT"),
            _("CONTAINER_ADDRESS"),
            _("IFACE_NAME"),
            _("IFACE_DESCRIPTION"),
            _("IFACE_SPEED"),
            _("MAX_LOAD_IN, Mbps"),
            _("MAX_LOAD_IN_TIME"),
            _("MAX_LOAD_OUT, Mbps"),
            _("MAX_LOAD_OUT_TIME"),
            _("AVG_LOAD_IN, Mbps"),
            _("AVG_LOAD_OUT, Mbps"),
            _("UPLINK_IFACE_NAME"),
            _("UPLINK_IFACE_DESCRIPTION"),
            _("UPLINK_MAX_LOAD_IN, Mbps"),
            _("UPLINK_MAX_TIME_IN"),
            _("UPLINK_MAX_LOAD_OUT, Mbps"),
            _("UPLINK_MAX_TIME_OUT"),
            _("UPLINK_AVG_LOAD_IN, Mbps"),
            _("UPLINK_AVG_LOAD_OUT, Mbps"),
            _("UPLINK_IFACE_SPEED"),
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
        columns_order = columns.split(",")
        columns_filter = set(columns_order)
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

        # Load managed objects
        mos = ManagedObject.objects.filter(is_managed=True)
        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        if selector:
            mos = mos.filter(ManagedObjectSelector.objects.get(id=int(selector)).Q)
        if administrative_domain:
            mos = mos.filter(
                administrative_domain__in=AdministrativeDomain.get_nested_ids(
                    int(administrative_domain)
                )
            )
        if object_profile:
            mos = mos.filter(object_profile=object_profile)
        if interface_profile:
            interface_profile = InterfaceProfile.objects.filter(id=interface_profile).first()

        mo_attrs = namedtuple("MOATTRs", [c for c in cols if c.startswith("object")])
        containers_address = {}
        if "object_container" in columns_filter:
            containers_address = ReportContainerData(set(mos.values_list("id", flat=True)))
            containers_address = dict(list(containers_address.extract()))

        moss = {}
        for row in mos.values_list(
            "id", "name", "address", "platform", "administrative_domain__name", "segment", "id"
        ):
            moss[row[0]] = mo_attrs(
                *[
                    row[1],
                    row[2],
                    str(Platform.get_by_id(row[3]) if row[3] else ""),
                    row[4],
                    str(NetworkSegment.get_by_id(row[5])) if row[5] else "",
                    containers_address.get(row[6], "") if containers_address and row[6] else "",
                ]
            )
        # get maximum metrics
        ifaces_metrics = get_interface_metrics(mos, from_date, to_date)

        for mm in ifaces_metrics:
            mo_id = moss[int(mm.id)]
            uplinks = set(mm.data.uplinks)
            links = []

            # find uplinks
            for l in Link.object_links(mm):
                local_interfaces = []
                remote_interfaces = []
                remote_objects = set()
                for ifs in l.interfaces:
                    if ifs.managed_object.id == mm.id:
                        local_interfaces += [ifs]
                    else:
                        remote_interfaces += [ifs]
                        remote_objects.add(ifs.managed_object)
                if len(remote_objects) == 1:
                    ro = remote_objects.pop()
                    if ro.id in uplinks:
                        role = "uplink"
                    else:
                        role = "downlink"
                    links += [
                        {
                            "id": l.id,
                            "role": role,
                            "local_interface": local_interfaces,
                            "remote_object": ro,
                            "remote_interface": remote_interfaces,
                            "remote_status": "up" if ro.get_status() else "down",
                        }
                    ]

            for i in ifaces_metrics[mm]:
                if not exclude_zero:
                    if (
                        ifaces_metrics[mm][i]["max_load_in"] == 0
                        and ifaces_metrics[mm][i]["max_load_out"] == 0
                    ):
                        continue
                if description:
                    if description not in ifaces_metrics[mm][i]["description"]:
                        continue
                if interface_profile:
                    if interface_profile.name not in ifaces_metrics[mm][i]["profile"]:
                        continue
                row2 = [
                    str(mm.id),
                    mm.name,
                    mm.address,
                    getattr(mo_id, "object_platform"),
                    getattr(mo_id, "object_adm_domain"),
                    getattr(mo_id, "object_segment"),
                    getattr(mo_id, "object_container"),
                    i,
                    ifaces_metrics[mm][i]["description"],
                    ifaces_metrics[mm][i]["bandwidth"],
                    ifaces_metrics[mm][i]["max_load_in"],
                    ifaces_metrics[mm][i]["max_load_in_time"],
                    ifaces_metrics[mm][i]["max_load_out"],
                    ifaces_metrics[mm][i]["max_load_out_time"],
                    ifaces_metrics[mm][i]["avg_load_in"],
                    ifaces_metrics[mm][i]["avg_load_out"],
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
                ss = True
                for link in links:
                    if link["role"] == "uplink":
                        ifname_uplink = link["local_interface"][0].name
                        if ifname_uplink in ifaces_metrics[mm]:
                            row2[16] = ifname_uplink
                            row2[17] = link["local_interface"][0].description
                            row2[22] = ifaces_metrics[mm][ifname_uplink]["avg_load_in"]
                            row2[23] = ifaces_metrics[mm][ifname_uplink]["avg_load_out"]
                            row2[18] = ifaces_metrics[mm][ifname_uplink]["max_load_in"]
                            row2[20] = ifaces_metrics[mm][ifname_uplink]["max_load_out"]
                            row2[19] = ifaces_metrics[mm][ifname_uplink]["max_load_in_time"]
                            row2[21] = ifaces_metrics[mm][ifname_uplink]["max_load_out_time"]
                            r += [translate_row(row2, cmap)]
                            ss = False
                if ss:
                    r += [translate_row(row2, cmap)]
        filename = "metrics_detail_report_%s" % datetime.datetime.now().strftime("%Y%m%d")
        if o_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="%s.csv"' % filename
            writer = csv.writer(response, dialect="excel", delimiter=",", quoting=csv.QUOTE_MINIMAL)
            writer.writerows(r)
            return response
        elif o_format == "xlsx":
            response = BytesIO()
            wb = xlsxwriter.Workbook(response)
            cf1 = wb.add_format({"bottom": 1, "left": 1, "right": 1, "top": 1})
            ws = wb.add_worksheet("Metrics")
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
