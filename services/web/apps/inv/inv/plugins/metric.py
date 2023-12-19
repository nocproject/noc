# ---------------------------------------------------------------------
# inv.inv metric plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from typing import List, Dict, Any

# NOC modules
from .base import InvPlugin
from noc.inv.models.sensor import Sensor
from noc.cm.models.configurationparam import ConfigurationParam
from noc.pm.models.metrictype import MetricType
from noc.sa.interfaces.base import DictListParameter
from noc.core.translation import ugettext as _


class MetricPlugin(InvPlugin):
    name = "metric"
    js = "NOC.inv.inv.plugins.metric.MetricPanel"

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
        mt = MetricType.get_by_id("Sensor | Value")
        for p in ConfigurationParam.objects.filter(metric_type=mt):
            d = o.get_cfg_data(param=p, scope=f"Sensor::{sensor.local_id}")
            if not d:
                continue
            r += [
                {
                    "value": d,
                    "op": ">",
                    "is_readonly": False,
                    "name": f"{p.code}@Sensor::{sensor.local_id}",
                    "description": "Threshold for Sensor",
                }
            ]
        return r

    def get_threshold_ranges(self, thresholds) -> List[Dict[str, Any]]:
        """
        "left": 50,
        "right": 120,
        "color": "#d2403d",
        #d2403d - critical
        #fce97d - warning
        """
        r = []
        for t in sorted(thresholds, key=operator.itemgetter("value")):
            ...
        return r

    def get_data(self, request, o):
        r = []
        for s in Sensor.objects.filter(
            object__in=[o.id] + [x[1] for x in o.iter_inner_connections()]
        ):
            components = [ll for ll in s.labels]
            if s.object != o:
                components.insert(0, f"object::{o.name}")
            thresholds = self.get_sensor_thresholds(o, s)
            ranges = self.get_threshold_ranges(thresholds)

            r.append(
                {
                    "bi_id": str(s.bi_id),
                    "id": str(s.id),
                    "name": str(s.local_id),
                    "component": ",".join(components),
                    "component__label": " ".join(components),
                    "units": str(s.units.id),
                    "units__label": s.units.name,
                    "value": 0,
                    "min_value": -100,
                    "max_value": 120,
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
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/$" % self.name,
            method=["POST"],
            validate={
                "thresholds": DictListParameter(required=True),
            },
        )

    def api_set_metric_threshold(self, request, oid, sid, thresholds):
        s = self.app.get_object_or_404(Sensor, id=sid)
        for t in thresholds:
            param = ConfigurationParam.get_by_code(t["name"])
            s.object.set_cfg_data(param, scope=f"Sensor::{s.local_id}")
        s.object.save()
        return {"success": True}
