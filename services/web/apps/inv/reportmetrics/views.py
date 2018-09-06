# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.reportmetrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
import datetime
import time
from collections import defaultdict
# Django modules
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.core.clickhouse.connect import connection
from noc.sa.models.useraccess import UserAccess
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.core.translation import ugettext as _
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.administrativedomain import AdministrativeDomain


class ReportForm(forms.Form):
    reporttype = forms.ChoiceField(choices=[
        ("load_interfaces", _("Load Interfaces")),
        ("load_cpu", _("Load CPU/Memory")),
        ("errors", _("Errors on the Interface")),
        ("ping", _("Ping RTT and Ping Attempts"))
    ], label=_("Report Type"))
    from_date = forms.CharField(
        widget=AdminDateWidget,
        label=_("From Date"),
        required=True
    )
    to_date = forms.CharField(
        widget=AdminDateWidget,
        label=_("To Date"),
        required=True
    )
    # skip_avail = forms.BooleanField(
    #     label=_("Skip full available"),
    #     required=False
    # )

    # managed_object = forms.ModelChoiceField(
    #    label=_("Managed Object"),
    #    required=False,
    #    queryset=ManagedObject.objects.filter()
    # )
    selectors = forms.ModelChoiceField(
        label=_("Selectors"),
        required=True,
        queryset=ManagedObjectSelector.objects.order_by("name")
    )
    administrative_domain = forms.ModelChoiceField(
        label=_("Administrative Domain (or)"),
        required=False,
        queryset=AdministrativeDomain.objects.order_by("name")
    )
    # object_profile = forms.ModelChoiceField(
    #    label=_("Object Profile"),
    #    required=False,
    #    queryset=ManagedObjectProfile.objects.exclude(name__startswith="tg.").order_by("name")
    # )
    interface_profile = forms.ModelChoiceField(
        label=_("Interface Profile (For Load Interfaces Report Type)"),
        required=False,
        queryset=InterfaceProfile.objects.order_by("name")
    )
    allow_archive = forms.BooleanField(
        label=_("Use archive (InfluxDB) for report"),
        required=False
    )
    zero = forms.BooleanField(
        label=_("Exclude 0"),
        required=False
    )
    percent = forms.BooleanField(
        label=_("Load interface in % (For Load Interfaces Report Type)"),
        required=False
    )
    filter_default = forms.BooleanField(
        label=_("Enable Default interface profile (For Load Interfaces Report Type)"),
        required=False
    )


class ReportMetric(object):
    CHUNK_SIZE = 10

    def __init__(self, db="ch"):
        self.rows = []
        self.get_query = self.get_query_inf
        self.query_map = ""
        self.reporttype = "load_interfaces"

    def get_query_inf(self, query_map, from_date, to_date):
        fd = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        td = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        map_table = {"load_interfaces": "/Interface\s\|\sLoad\s\|\s[In|Out]/",
                     "load_cpu": "/[CPU|Memory]\s\|\sUsage/",
                     "errors": "/Interface\s\|\s[Errors|Discards]\s\|\s[In|Out]/",
                     "ping": "/Ping\s\|\sRTT/"}
        def_map = {"q_select": ['percentile(\"value\", 98)'],
                   "q_from": [],  # q_from = "from %s" % map_table[reporttype]
                   "q_where": ["%s", "time >= '%s'" % fd, "time <= '%s'" % td],
                   "q_group": ["object"]}
        # m_r = "(%s)" % " OR ".join(["object = '%s'" % name for name in moss])
        for e in query_map:
            if e.startswith("q_"):
                def_map[e] += query_map[e]
        query = " ".join(["SELECT %s" % ",".join(def_map["q_select"]),
                          "FROM %s" % map_table[self.reporttype],
                          "WHERE %s" % " AND ".join(def_map["q_where"]),
                          "GROUP BY %s" % ",".join(def_map["q_group"])])
        return query

    def get_query_ch(self, query_map, from_date, to_date):
        ts_from_date = time.mktime(from_date.timetuple())
        ts_to_date = time.mktime(to_date.timetuple())
        map_table = {"load_interfaces": "interface",
                     "load_cpu": "cpu",
                     "errors": "interface",
                     "ping": "ping"}
        def_map = {"q_select": ["managed_object"],
                   "q_from": [],  # q_from = "from %s" % map_table[reporttype]
                   "q_where": ["(ts >= toDateTime(%d) AND ts <= toDateTime(%d))" %
                               (ts_from_date, ts_to_date)],
                   "q_group": ["managed_object"]}
        for e in query_map:
            if e.startswith("q_"):
                def_map[e] += query_map[e]
        query = " ".join(["select %s" % ",".join(def_map["q_select"]),
                          "from %s" % map_table[self.reporttype],
                          "prewhere %s" % "date >= toDate(%d) AND date <= toDate(%d) AND %s" % (
                              ts_from_date, ts_to_date, "managed_object IN (%s)"),
                          "where %s" % " AND ".join(def_map["q_where"]),
                          "group by %s" % ",".join(def_map["q_group"])])
        return query

    def do_query_ch(self, moss, query_map, f_date, to_date):
        n = 0
        client = connection()

        mos_name = sorted(moss)
        query = self.get_query_ch(query_map, f_date, to_date)
        self.CHUNK_SIZE = 4000
        while mos_name:
            mos_name, m_r = mos_name[self.CHUNK_SIZE:], mos_name[:self.CHUNK_SIZE]
            for row in client.execute(query % ", ".join(m_r)):
                yield row[0:2], row[2:]
            n += 1

    def do_query(self, moss, query_map, f_date, to_date):
        n = 0
        ex_res = defaultdict(list)

        client = None
        mos_name = moss.keys()
        query = self.get_query(query_map, f_date, to_date)
        while mos_name[n:n + self.CHUNK_SIZE]:
            m_r = "(%s)" % " OR ".join(["object = '%s'" % name for name in mos_name[n:n + self.CHUNK_SIZE]])
            # print query % m_r

            for row in client.query(query % m_r):
                if self.reporttype in ["ping", "load_cpu"]:
                    ex_res[(row["object"],)] += [row["percentile"]]
                else:
                    ex_res[(row["object"], row["interface"])] += [row["percentile"]]
            n += self.CHUNK_SIZE
        for ll in ex_res:
            yield ll, ex_res[ll]


class ReportTraffic(SimpleReport):
    title = _("Load Metrics")
    form = ReportForm

    def get_data(self, request, reporttype=None, from_date=None, to_date=None, object_profile=None, percent=None,
                 filter_default=None, zero=None, interface_profile=None, managed_object=None,
                 selectors=None, administrative_domain=None, allow_archive=True, **kwargs):

        map_table = {"load_interfaces": "/Interface\s\|\sLoad\s\|\s[In|Out]/",
                     "load_cpu": "/[CPU|Memory]\s\|\sUsage/",
                     "errors": "/Interface\s\|\s[Errors|Discards]\s\|\s[In|Out]/",
                     "ping": "/Ping\s\|\sRTT/"}

        # Date Time Block
        if not from_date:
            from_date = datetime.datetime.now() - datetime.timedelta(days=1)
        else:
            from_date = datetime.datetime.strptime(from_date, "%d.%m.%Y")

        if not to_date or from_date == to_date:
            to_date = from_date + datetime.timedelta(days=1)
        else:
            to_date = datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)

        interval = (to_date - from_date).days
        ts_from_date = time.mktime(from_date.timetuple())
        ts_to_date = time.mktime(to_date.timetuple())

        # Load managed objects
        mos = ManagedObject.objects.filter(is_managed=True)
        if not request.user.is_superuser:
            mos = mos.filter(
                administrative_domain__in=UserAccess.get_domains(request.user))
        if managed_object:
            mos = [managed_object]
        else:
            if selectors:
                mos = mos.filter(selectors.Q)
            if administrative_domain:
                # @todo fix
                mos = mos.filter(administrative_domain=administrative_domain)
            if object_profile:
                mos = mos.filter(object_profile=object_profile)

        columns = [_("Managed Object"), _("Address")]
        iface_dict = {}

        d_url = {
            "path": "/ui/grafana/dashboard/script/report.js",
            "rname": map_table[reporttype],
            "from": str(int(ts_from_date * 1000)),
            "to": str(int(ts_to_date * 1000)),
            # o.name.replace("#", "%23")
            "biid": "",
            "oname": "",
            "iname": ""}

        report_map = {
            "load_interfaces": {
                "url": '%(path)s?title=interface&biid=%(biid)s'
                       '&obj=%(oname)s&iface=%(iname)s&from=%(from)s&to=%(to)s',
                "q_group": ["interface"],
                "columns": [_("Int Name"), _("Int Descr"),
                            TableColumn(_("IN bps"), align="right"),
                            TableColumn(_("OUT bps"), align="right"),
                            ]
            },
            "errors": {
                "url": """%(path)s?title=errors&biid=%(biid)s&obj=%(oname)s&iface=%(iname)s&from=%(from)s&to=%(to)s""",
                "columns": [_("Int Name"),
                            TableColumn(_("Errors IN"), align="right"),
                            TableColumn(_("Errors OUT"), align="right"),
                            TableColumn(_("Discards IN"), align="right"),
                            TableColumn(_("Discards OUT"), align="right")],
                "q_group": ["interface"]
            },
            "load_cpu": {
                "url": """%(path)s?title=cpu&biid=%(biid)s&obj=%(oname)s&from=%(from)s&to=%(to)s""",
                "columns": [TableColumn(_("Memory | Usage %"), align="right"),
                            TableColumn(_("CPU | Usage %"), align="right")]
            },
            "ping": {
                "url": """%(path)s?title=ping&biid=%(biid)s&obj=%(oname)s&from=%(from)s&to=%(to)s""",
                "columns": [TableColumn(_("Ping | RTT (ms)"), align="right"),
                            TableColumn(_("Ping | Attempts"), align="right")]
            }
        }
        if not allow_archive:
            report_map["load_interfaces"].update({
                "q_select": ["arrayStringConcat(path)",
                             "round(quantile(0.98)(load_in), 0) as l_in",
                             "round(quantile(0.98)(load_out), 0) as l_out"],
                "q_group": ["path"],
                "q_where": ["(load_in != 0 and load_out != 0)"] if zero else []})
            report_map["errors"].update({
                "q_select": ["arrayStringConcat(path)",
                             "quantile(0.98)(errors_in) as err_in", "quantile(0.98)(errors_out) as err_out",
                             "quantile(0.98)(discards_in) as dis_in", "quantile(0.98)(discards_out) as dis_out"],
                "q_group": ["path"],
                "q_where": ["(errors_in != 0 or errors_out != 0 or discards_in != 0 or discards_out != 0)"] if zero
                else []})
            report_map["load_cpu"].update({"q_select": ["arrayStringConcat(path)", "quantile(0.98)(usage) as usage"],
                                           "q_group": ["path"]})
            report_map["ping"].update({
                "q_select": ["managed_object", "round(quantile(0.98)(rtt) / 1000, 2)", "avg(attempts)"]})
            moss = {str(mo[0]): mo for mo in mos.values_list("bi_id", "id", "name", "address")}
        else:
            moss = {mo[0]: mo for mo in mos.values_list("name", "id", "name", "address")}
        # mos_s = set(mos.values_list("id", flat=True))
        if reporttype in ["load_interfaces", "errors"]:
            ifaces = Interface._get_collection()
            xx = set(mos.values_list("id", flat=True))
            for iface in ifaces.find(
                    {"type": "physical"},
                    {"managed_object": 1, "name": 1, "description": 1, "in_speed": 1, "out_speed": 1}):
                if iface["managed_object"] not in xx:
                    continue
                iface_dict[(iface["managed_object"],
                            iface["name"])] = (iface.get("description", ""),
                                               iface.get("in_speed", 0), iface.get("out_speed", 0))

        columns += report_map[reporttype]["columns"]
        if percent:
            columns.insert(-1, TableColumn(_("IN %"), align="right"))
            columns += [TableColumn(_("OUT %"), align="right")]
        columns += [TableColumn(_("Graphic"), format="url"),
                    TableColumn(_("Interval days"), align="right")
                    ]
        url = report_map[reporttype].get("url", "")
        rm = ReportMetric()
        rm.reporttype = reporttype

        r = []
        if allow_archive:
            rm_data = rm.do_query(moss, report_map[reporttype], from_date, to_date)
        else:
            rm_data = rm.do_query_ch(moss, report_map[reporttype], from_date, to_date)

        for l, data in rm_data:
            if not l:
                continue
            mo = moss[l[0]]
            d_url["biid"] = l[0]
            d_url["oname"] = mo[2].replace("#", "%23")
            if zero and allow_archive and not sum(data):
                # For InfluxDB query
                continue
            if reporttype in ["load_interfaces", "errors"]:
                d_url["iname"] = l[1]
                res = [mo[2], mo[3], l[1]]
                res += data
                if "load_interfaces" in reporttype:
                    i_d = iface_dict.get((mo[1], l[1]), ["", "", ""])
                    res.insert(3, i_d[0])
                    if percent:
                        in_p = float(data[0])
                        in_p = round((in_p / 1000.0) / (i_d[1] / 100.0), 2) if i_d[1] and in_p > 0 else 0
                        # in
                        res.insert(-1, in_p)
                        # out
                        out_p = float(data[1])
                        res += [round((out_p / 1000.0) / (i_d[2] / 100.0), 2) if i_d[2] and out_p > 0 else 0]
            else:
                res = [mo[2], mo[3]]
                res += data
            res += [url % d_url, interval]
            r += [res]

        return self.from_dataset(
            title=self.title,
            columns=columns,
            data=r,
            enumerate=True
        )
