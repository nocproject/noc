# ----------------------------------------------------------------------
# fm.reportettsystemstat
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import time

# Third-party modules
from django import forms
from django.forms import widgets
from django.contrib.admin.widgets import AdminDateWidget

# NOC modules
from noc.services.web.base.simplereport import SimpleReport, PredefinedReport, SectionRow
from noc.core.clickhouse.connect import connection
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.ttsystem import TTSystem
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    repo_format = forms.ChoiceField(
        label="Формат отчёта",
        widget=widgets.RadioSelect,
        choices=((0, "Статистика"), (1, "Детализация ошибок эскалации")),
        initial=0,
        required=False,
    )
    interval = forms.ChoiceField(
        choices=[(0, _("Range")), (1, _("1 day")), (7, _("1 week")), (30, _("1 month"))],
        label=_("Interval"),
    )
    from_date = forms.CharField(widget=AdminDateWidget, label=_("From Date"), required=False)
    to_date = forms.CharField(widget=AdminDateWidget, label=_("To Date"), required=False)


class ReportTTSystemStatApplication(SimpleReport):
    title = _("TT system statistics")
    form = ReportForm
    predefined_reports = {
        "1d": PredefinedReport(_("TTSystem Stat (1 day)"), {"interval": 1}),
        "7d": PredefinedReport(_("TTSystem Stat (7 days)"), {"interval": 7}),
        "30d": PredefinedReport(_("TTSystem Stat (30 day)"), {"interval": 30}),
        "1d_errors": PredefinedReport(
            _("TTSystem Errors (1 day)"), {"interval": 1, "repo_format": "1"}
        ),
    }

    def get_data(self, request, interval=1, repo_format=0, from_date=None, to_date=None, **kwargs):
        # Date Time Block
        if from_date:
            from_date = datetime.datetime.strptime(from_date, "%d.%m.%Y")
        elif interval:
            from_date = datetime.datetime.now() - datetime.timedelta(days=int(interval))
        else:
            from_date = datetime.datetime.now() - datetime.timedelta(days=1)

        if to_date:
            to_date = datetime.datetime.strptime(to_date, "%d.%m.%Y")
            if from_date == to_date:
                to_date = from_date + datetime.timedelta(days=1)
        elif interval:
            to_date = from_date + datetime.timedelta(days=int(interval))
        else:
            to_date = from_date + datetime.timedelta(days=1)
        columns = [
            _("Server"),
            _("Service"),
            _("Request count"),
            _("Success request count"),
            _("Failed request count"),
            _("Success request (%)"),
            _("Q1 (ms)"),
            _("Q2 (ms)"),
            _("Q3 (ms)"),
            _("p95 (ms)"),
            _("max (ms)"),
        ]
        if repo_format == "1":
            columns = [
                _("Timestamp"),
                _("Server"),
                _("Service"),
                _("Managed Object"),
                _("TT ID"),
                _("Error code"),
                _("Error text"),
            ]
        ts_from_date = time.mktime(from_date.timetuple())
        ts_to_date = time.mktime(to_date.timetuple())

        tt_systems = TTSystem.objects.filter().scalar("name")
        # Manged Object block

        q1 = """select server, service, count(), round(quantile(0.25)(duration), 0)/1000 as q1,
                                        round(quantile(0.5)(duration), 0)/1000 as q2,
                                        round(quantile(0.75)(duration), 0)/1000 as q3,
                                        round(quantile(0.95)(duration),0)/1000 as p95,
                                        round(max(duration),0)/1000 as max from span where %s
                                        group by server, service"""

        q2 = """select server, service, error_code, count(), avg(duration)
                from span where %s group by server, service, error_code"""

        q3 = """select ts, server, service, in_label, in_label, error_code, error_text from span
                where service IN ('create_massive_damage_outer', 'change_massive_damage_outer_close') and
                      error_code <> 0 and %s"""

        q_where = ["server IN ('%s')" % "', '".join(tt_systems)]
        # q_where = ["managed_object IN (%s)" % ", ".join(mo_bi_dict.keys())]
        q_where += [
            "(date >= toDate(%d)) AND (ts >= toDateTime(%d) AND ts <= toDateTime(%d))"
            % (ts_from_date, ts_from_date, ts_to_date)
        ]
        r = []
        ch = connection()
        if repo_format == "1":
            aa = {
                aa.escalation_tt.split(":")[-1]: aa
                for aa in ArchivedAlarm.objects.filter(
                    clear_timestamp__gte=from_date,
                    clear_timestamp__lte=to_date,
                    escalation_tt__exists=True,
                )
            }
            query = q3 % " and ".join(q_where)
            for row in ch.execute(query):
                if row[2] in ["create_massive_damage_outer"]:
                    row[2] = "Создание ТТ"
                    try:
                        row[3] = ManagedObject.objects.get(tt_system_id=int(row[3]))
                        row[4] = ""
                    except ManagedObject.DoesNotExist:
                        pass
                    except ManagedObject.MultipleObjectsReturned:
                        row[3] = ManagedObject.objects.get(
                            tt_system_id=int(row[3]), is_managed=True
                        )
                        row[4] = ""
                elif row[2] in ["change_massive_damage_outer_close"]:
                    row[2] = "Закрытие ТТ"
                    row[4] = row[3]
                    row[3] = aa[row[3]].managed_object if row[3] in aa else row[3]
                else:
                    continue
                r += [row]
        else:
            query = q1 % " and ".join(q_where)
            # (server, service)
            tt_s = {}
            for row in ch.execute(query):
                tt_s[(row[0], row[1])] = [row[2]] + [0, 0, 0] + row[3:]
            query = q2 % " and ".join(q_where)
            for row in ch.execute(query):
                if row[2] == "0":
                    tt_s[(row[0], row[1])][1] = row[3]
                else:
                    tt_s[(row[0], row[1])][2] += int(row[3])

            r += [
                SectionRow(
                    name="Report from %s to %s"
                    % (from_date.strftime("%d.%m.%Y %H:%M"), to_date.strftime("%d.%m.%Y %H:%M"))
                )
            ]
            for line in sorted(tt_s, key=lambda x: x[0]):
                data = list(line)
                data += tt_s[line]
                data[5] = round((float(data[3]) / float(data[2])) * 100.0, 2)
                r += [data]

        return self.from_dataset(title=self.title, columns=columns, data=r, enumerate=True)
