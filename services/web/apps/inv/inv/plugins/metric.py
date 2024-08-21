# ---------------------------------------------------------------------
# inv.inv metric plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
import datetime

# Python modules
import operator
from typing import List, Dict, Any, Tuple, Optional

# Third-party modules
import orjson

# NOC modules
from .base import InvPlugin
from noc.inv.models.sensor import Sensor
from noc.cm.models.configurationparam import ConfigurationParam
from noc.pm.models.metrictype import MetricType
from noc.sa.interfaces.base import DictListParameter, StringParameter, FloatParameter
from noc.core.translation import ugettext as _
from noc.core.clickhouse.connect import connection


class MetricPlugin(InvPlugin):
    name = "metric"
    js = "NOC.inv.inv.plugins.metric.MetricPanel"

    def get_sensor_values(self) -> Dict[int, float]:
        r = {}
        ch = connection()
        now = datetime.datetime.now().replace(microsecond=0)
        query = ch.execute(
            """
            SELECT sensor, argMax(value, ts) AS v
            FROM sensor
            WHERE date >= %s
            GROUP BY sensor
            FORMAT JSONEachRow
            """,
            return_raw=True,
            args=[now.date().isoformat()],
        )
        for d in query.splitlines():
            d = orjson.loads(d)
            r[int(d["sensor"])] = float(d["v"])
        return r

    def get_position(self, value, p_start, p_end, a_start, a_end) -> float:
        """
        Getting relative value position, by formula x = a + ((b - a) * c / 100)
        """
        relative_value = value / (a_end - a_start) * 100
        return round(p_start + ((p_end - p_start) * relative_value) / 100, 2)

    def get_sensor_thresholds(self, o, sensor: "Sensor"):
        """
        disabled, ok, warning (degraded), critical
        # value
        # position (percent)
        # is_readonly
        # name
        # description
        """
        r = []
        mt = MetricType.get_by_name("Sensor | Value")
        for p in ConfigurationParam.objects.filter(metric_type=mt):
            d = o.get_cfg_data(param=p, scope=f"Sensor::{sensor.local_id}")
            if not d:
                continue
            r += [
                {
                    "value": d,
                    "relative_position": 10,  # Percent
                    "op": p.threshold_op,
                    "is_readonly": False,
                    "name": f"{p.code}@Sensor::{sensor.local_id}",
                    "label": f"{sensor.local_id}{p.code}",
                    "description": "Threshold for Sensor",
                }
            ]
        return r

    def get_threshold_ranges(
        self, thresholds, value
    ) -> Tuple[Optional[int], Optional[int], float, List[Dict[str, Any]]]:
        """
        Getting Thresholds Value Ranges, Caclculate if value has settings thresholds
        "left": 50,
        "right": 120,
        "color": "#d2403d",
        #d2403d - critical
        #fce97d - warning
        """
        if value is None:
            return None, None, 50, []
        r = []
        left = sorted([t for t in thresholds if t["op"] == "<="], key=operator.itemgetter("value"))
        right = sorted([t for t in thresholds if t["op"] == ">="], key=operator.itemgetter("value"))
        min_value = min(value, left[0]["value"] if left else value) - 10
        max_value = max(value, right[-1]["value"] if right else value) + 10
        if len(left) == 1:
            left[0]["relative_position"] = 10
            r += [
                {
                    "left": min_value,
                    "right": left[0]["value"],
                    "relative_position": {
                        "left": 0,
                        "right": 10,
                    },
                    "color": "#d2403d",
                }
            ]
        elif len(left) > 1:
            left[0]["relative_position"] = 10
            left[-1]["relative_position"] = 30
            r += [
                {
                    "left": min_value,
                    "right": left[0]["value"],
                    "relative_position": {
                        "left": 0,
                        "right": 10,
                    },
                    "color": "#d2403d",
                },
                {
                    "left": left[0]["value"],
                    "right": left[-1]["value"],
                    "relative_position": {
                        "left": 10,
                        "right": 30,
                    },
                    "color": "#fce97d",
                },
            ]
        if len(right) == 1:
            right[0]["relative_position"] = 90
            r += [
                {
                    "left": right[0]["value"],
                    "right": max_value,
                    "relative_position": {
                        "left": 90,
                        "right": 100,
                    },
                    "color": "#d2403d",
                }
            ]
        elif len(right) > 1:
            right[0]["relative_position"] = 70
            right[-1]["relative_position"] = 90
            r += [
                {
                    "left": right[0]["value"],
                    "right": right[-1]["value"],
                    "relative_position": {
                        "left": 70,
                        "right": 90,
                    },
                    "color": "#fce97d",
                },
                {
                    "left": right[-1]["value"],
                    "right": max_value,
                    "relative_position": {
                        "left": 90,
                        "right": 100,
                    },
                    "color": "#d2403d",
                },
            ]
        # Calculate relative value
        absolute_start, absolute_end = min_value, max_value  # Absolute_start, Absolute end
        relative_start, relative_end = 0, 100  #
        for num, x in enumerate(r, start=1):
            if num == 1 and value < x["left"]:
                relative_end = x["relative_position"]["right"]
                absolute_end = x["left"]["right"]
                break
            elif x["left"] < value < x["right"]:
                relative_start, relative_end = (
                    x["relative_position"]["left"],
                    x["relative_position"]["right"],
                )
                absolute_start, absolute_end = x["left"], x["right"]
                break
            elif len(r) == num and value > x["right"]:
                relative_start = x["relative_position"]["left"]
                absolute_start = x["left"]
                break
        return (
            min_value,
            max_value,
            self.get_position(value, relative_start, relative_end, absolute_start, absolute_end),
            r,
        )

    def get_data(self, request, o):
        """
        Getting Object sensors
        """
        r = []
        values = self.get_sensor_values()
        print(values)
        for s in Sensor.objects.filter(object__in=[o.id] + [x for x in o.iter_children()]):
            components = [ll for ll in s.labels]
            if s.object != o:
                components.insert(0, f"object::{o.name}")
            thresholds = self.get_sensor_thresholds(o, s)
            value = values.get(s.bi_id)
            min_value, max_value, position, ranges = self.get_threshold_ranges(thresholds, value)
            r.append(
                {
                    "bi_id": str(s.bi_id),
                    "id": str(s.id),
                    "object": str(o.id),
                    "object__label": o.name,
                    "name": str(s.local_id),
                    "component": ",".join(components),
                    "component__label": " ".join(components),
                    "units": str(s.units.id),
                    "units__label": s.units.name,
                    "value": value,
                    "min_value": min_value,
                    "max_value": max_value,
                    "relative_position": position,
                    "oper_state": "ok",
                    "oper_state__label": _("OK"),
                    # "description": s.description,
                    # disabled, ok, warning (degraded), critical
                    "thresholds": thresholds,
                    "ranges": ranges,
                }
            )
        return r

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            "api_plugin_%s_set_metric_threshold" % self.name,
            self.api_set_metric_threshold,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/(?P<sid>[0-9a-f]{24})/set_threshold/$" % self.name,
            method=["POST"],
            validate={
                "thresholds": DictListParameter(
                    required=True,
                    attrs={
                        "name": StringParameter(required=True),
                        "value": FloatParameter(required=True),
                        "op": StringParameter(required=False),
                    },
                ),
            },
        )

    def api_set_metric_threshold(self, request, id, sid, thresholds):
        s = self.app.get_object_or_404(Sensor, id=sid)
        for t in thresholds:
            param, scope = t["name"].split("@", 1)
            param = ConfigurationParam.get_by_code(param)
            print("Set Threshold", param, f"Sensor::{s.local_id}", t["value"])
            if t["value"] != s.object.get_cfg_data(param, scope=scope):
                s.object.set_cfg_data(param, t["value"], scope=scope)
        s.object.save()
        return {"success": True}
