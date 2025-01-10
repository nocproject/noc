# ---------------------------------------------------------------------
# Object card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.errors import DoesNotExist

# NOC modules
import datetime
import operator
import itertools
from collections import defaultdict
from .base import BaseCard
from noc.inv.models.object import Object
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.uptime import Uptime
from noc.fm.models.outage import Outage
from noc.core.perf import metrics
from noc.core.pm.utils import is_nan
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType
from noc.core.clickhouse.connect import connection


class ObjectCard(BaseCard):
    name = "object"
    default_template_name = "object"
    model = Object

    def get_object(self, id):
        return Object.objects.get(id=id)

    def get_data(self):
        if not self.object:
            return None

        # Get path
        path = [{"id": self.object.id, "name": self.object.name}]
        c = getattr(self.object.container, "id", None)
        while c:
            try:
                c = Object.get_by_id(c)
                if not c:
                    break
                if c.container:
                    path.insert(0, {"id": c.id, "name": c.name})
                c = c.container.id if c.container else None
            except DoesNotExist:
                metrics["error", ("type", "no_such_object")] += 1
                break

        # Get children
        children = []
        for o in ManagedObject.objects.filter(container=self.object.id):
            # Alarms
            now = datetime.datetime.now()
            # Get object status and uptime
            alarms = list(ActiveAlarm.objects.filter(managed_object=o.id))
            current_state = None
            current_start = None
            duration = None

            uptime = Uptime.objects.filter(object=o.id, stop=None).first()

            if uptime:
                current_start = uptime.start
            else:
                current_state = "down"
                outage = Outage.objects.filter(object=o.id, stop=None).first()

                if outage:
                    current_start = outage.start

            if current_start:
                duration = now - current_start

            # Alarms detailed information
            alarm_list = []
            for alarm in alarms:
                alarm_list += [
                    {
                        "id": alarm.id,
                        "timestamp": alarm.timestamp,
                        "duration": now - alarm.timestamp,
                        "subject": alarm.subject,
                    }
                ]
            alarm_list = sorted(alarm_list, key=operator.itemgetter("timestamp"))

            # Metrics
            metric_map = self.get_metrics([o])
            metric_map = metric_map[o]

            children += [
                {
                    "id": o.id,
                    "name": o.name,
                    "address": o.address,
                    "platform": o.platform.name if o.platform else "Unknown",
                    "version": o.version.version if o.version else "",
                    "description": o.description,
                    "object_profile": o.object_profile.id,
                    "object_profile_name": o.object_profile.name,
                    "segment": o.segment,
                    #
                    "current_state": current_state,
                    # Start of uptime/downtime
                    "current_start": current_start,
                    # Current uptime/downtime
                    "current_duration": duration,
                    "alarms": alarm_list,
                    "metrics": metric_map["object"],
                }
            ]

        contacts_list = []

        if self.object.get_data("contacts", "technical") is not None and len(contacts_list) > 0:
            contacts_list.append({"Technical": self.object.get_data("contacts", "technical")})
        elif self.object.get_data("contacts", "technical") is not None:
            contacts_list.append({"Technical": self.object.get_data("contacts", "technical")})

        if (
            self.object.get_data("contacts", "administrative") is not None
            and len(contacts_list) > 0
        ):
            contacts_list.insert(
                0, {"Administrative": self.object.get_data("contacts", "administrative")}
            )
        elif self.object.get_data("contacts", "administrative") is not None:
            contacts_list.append(
                {"Administrative": self.object.get_data("contacts", "administrative")}
            )

        if self.object.get_data("contacts", "billing") is not None and len(contacts_list) > 0:
            contacts_list.insert(1, {"Billing": self.object.get_data("contacts", "billing")})
        elif self.object.get_data("contacts", "billing") is not None:
            contacts_list.append({"Billing": self.object.get_data("contacts", "billing")})

        return {
            "object": self.object,
            "path": path,
            "location": self.object.get_data("address", "text"),
            "contacts": contacts_list,
            "id": self.object.id,
            "name": self.object.name,
            "children": children,
        }

    @staticmethod
    def get_metrics(mos):
        from_date = datetime.datetime.now() - datetime.timedelta(days=1)
        from_date = from_date.replace(microsecond=0)
        # mo = self.object
        bi_map = {str(mo.bi_id): mo for mo in mos}
        SQL = """SELECT managed_object, arrayStringConcat(path) as iface, argMax(ts, ts), argMax(load_in, ts), argMax(load_out, ts), argMax(errors_in, ts), argMax(errors_out, ts)
                FROM interface
                WHERE
                  date >= toDate('%s')
                  AND ts >= toDateTime('%s')
                  AND managed_object IN (%s)
                GROUP BY managed_object, iface
                """ % (
            from_date.date().isoformat(),
            from_date.isoformat(sep=" "),
            ", ".join(bi_map),
        )
        ch = connection()
        mtable = []  # mo_id, mac, iface, ts
        last_ts = {}  # mo -> ts
        metric_map = {
            mo: {"interface": defaultdict(dict), "object": defaultdict(dict)} for mo in mos
        }
        msd = {ms.id: ms.table_name for ms in MetricScope.objects.filter()}
        mts = {
            str(mt.id): (msd[mt.scope.id], mt.field_name, mt.name)
            for mt in MetricType.objects.all()
        }
        # Interface Metrics
        for mo_bi_id, iface, ts, load_in, load_out, errors_in, errors_out in ch.execute(post=SQL):
            mo = bi_map.get(mo_bi_id)
            if mo:
                if is_nan(load_in, load_out, errors_in, errors_out):
                    continue
                mtable += [[mo, iface, ts, load_in, load_out]]
                metric_map[mo]["interface"][iface] = {
                    "load_in": int(load_in),
                    "load_out": int(load_out),
                    "errors_in": int(errors_in),
                    "errors_out": int(errors_out),
                }
                last_ts[mo] = max(ts, last_ts.get(mo, ts))

        # Object Metrics
        # object_profiles = set(mos.values_list("object_profile", flat=True))
        object_profiles = set(mo.object_profile.id for mo in mos)
        mmm = set()
        op_fields_map = defaultdict(list)
        for op in ManagedObjectProfile.objects.filter(id__in=object_profiles):
            for mt in op.metrics or []:
                mmm.add(mts[mt["metric_type"]])
                op_fields_map[op.id] += [mts[mt["metric_type"]][1]]

        for table, fields in itertools.groupby(sorted(mmm, key=lambda x: x[0]), key=lambda x: x[0]):
            # tb_fields = [f[1] for f in fields]
            # mt_name = [f[2] for f in fields]
            fields = list(fields)
            SQL = """SELECT managed_object, argMax(ts, ts), %s
                  FROM %s
                  WHERE
                    date >= toDate('%s')
                    AND ts >= toDateTime('%s')
                    AND managed_object IN (%s)
                  GROUP BY managed_object
                  """ % (
                ", ".join(["argMax(%s, ts) as %s" % (f[1], f[1]) for f in fields]),
                table,
                from_date.date().isoformat(),
                from_date.isoformat(sep=" "),
                ", ".join(bi_map),
            )
            # print SQL
            for result in ch.execute(post=SQL):
                mo_bi_id, ts = result[:2]
                mo = bi_map.get(mo_bi_id)
                i = 0
                for r in result[2:]:
                    f_name = fields[i][2]
                    mtable += [[mo, ts, r]]
                    metric_map[mo]["object"][f_name] = r
                    last_ts[mo] = max(ts, last_ts.get(mo, ts))
                    i += 1
        return metric_map
