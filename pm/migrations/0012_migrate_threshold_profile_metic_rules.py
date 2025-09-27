# ---------------------------------------------------------------------
# Migrate ThresholdProfiles to MetricAction
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Literal, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass

# Third-party modules
import bson
import orjson
import uuid
from pymongo import InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration

function_map = {
    "last": (None, None),
    "sum": (None, None),
    "avg": ("mean", {}),
    "percentile": ("percentile", {}),
    "q1": ("percentile", {"percentile": 25}),
    "q2": ("percentile", {"percentile": 50}),
    "q3": ("percentile", {"percentile": 75}),
    "p95": ("percentile", {"percentile": 95}),
    "p99": ("percentile", {"percentile": 99}),
    "step_inc": ("sumstep", {"direction": "inc"}),
    "step_dec": ("sumstep", {"direction": "dec"}),
    "step_abs": ("sumstep", {"direction": "abs"}),
    "exp_decay": ("exp_decay", {}),
}


@dataclass
class ThresholdProfile(object):
    window_type: str
    window_size: int
    window_func: Optional[str]
    value: float
    condition: Literal["<", ">", "<=", ">="]
    clear_value: Optional[float]
    clear_condition: Optional[Literal["<", ">", "<=", ">="]]

    def get_function(self):
        if not self.window_func:
            return None
        func, *param = function_map.get(self.window_func)
        return func

    def get_activate(self) -> Tuple[float, Optional[float], bool]:
        """
        Convert clear value to activation_level
        :return: activation_level, deactivation_level, inverse
        """
        inverse = False
        if self.condition in ["<", "<="]:
            # Inverse condition for level
            inverse = True
        value, clear_value = self.value, self.clear_value
        if "=" in self.clear_condition and not inverse:
            clear_value += 1
        elif "=" in self.clear_condition and inverse:
            clear_value -= 1
        if "=" not in self.condition and not inverse:
            value += 1
        elif "=" not in self.condition and inverse:
            value -= 1
        if value == clear_value:
            return value, None, inverse
        return value, clear_value, inverse

    def get_window_config(self):
        if not self.window_func:
            return None
        func, config = function_map.get(self.window_func)
        if not func:
            return None
        return {
            "max_window": self.window_size,
            "min_window": self.window_size,
            "window_config": config,
            "window_function": func,
            "window_type": self.window_type,
        }

    def get_alarm_config(self):
        al, dl, inverse = self.get_activate()
        r = {
            "activation_level": float(al),
            "alarm_class": "NOC | PM | Out of Thresholds Interface",
            "reference": None,
        }
        if inverse:
            r["invert_condition"] = "true"
        if dl is not None:
            r["deactivation_level"] = float(dl)
        return r


class Migration(BaseMigration):
    depends_on = [("sa", "0229_managedobjectprofile_metrics_jsonb")]

    def get_metric_action(self, metric_type, settings, num=None):
        r = {
            "_id": bson.ObjectId(),
            "name": f"Metric rule for {metric_type} ({num or ''})",
            # "$collection": "pm.metricactions",
            "uuid": uuid.uuid4(),
            "params": [
                {"name": "alarm.invert_condition", "description": None, "type": "bool"},
                {
                    "name": "alarm.activation_level",
                    "description": None,
                    "max_value": 1.0,
                    "min_value": 1.0,
                    "type": "float",
                },
                {
                    "name": "alarm.deactivation_level",
                    "description": None,
                    "max_value": 1.0,
                    "min_value": 1.0,
                    "type": "float",
                },
                {
                    "name": "activation-window.min_window",
                    "description": None,
                    "max_value": 2,
                    "min_value": 1,
                    "type": "int",
                },
                {
                    "name": "activation-window.max_window",
                    "description": None,
                    "max_value": 2,
                    "min_value": 1,
                    "type": "int",
                },
            ],
            "compose_inputs": [{"input_name": "in", "metric_type": metric_type}],
            "alarm_config": {
                "alarm_class": "NOC | PM | Out of Thresholds Interface",
                "reference": None,
            },
        }
        if settings:
            r["activation_config"] = settings
            r["name"] += f" for function {settings['window_function']}"
        return r

    def migrate(self):
        thps = {}
        for rp in self.mongo_db["thresholdprofiles"].find():
            if not rp.get("thresholds"):
                continue
            thps[str(rp["_id"])] = ThresholdProfile(
                window_type={"m": "tick", "t": "seconds"}.get(rp["window_type"]),
                window_size=rp.get("window", 1),
                window_func=rp.get("window_function", "last"),
                value=rp["thresholds"][0]["value"],
                condition=rp["thresholds"][0]["op"],
                clear_value=rp["thresholds"][0].get("clear_value"),
                clear_condition=rp["thresholds"][0].get("clear_op"),
            )

        interface_profiles = self.mongo_db["noc.interface_profiles"]
        thresholds = defaultdict(list)
        for ip in interface_profiles.find({"metrics.threshold_profile": {"$exists": True}}):
            for m in ip["metrics"]:
                if not m.get("threshold_profile"):
                    continue
                thresholds[(str(m["threshold_profile"]), m["metric_type"])] += [
                    f"noc::interface_profile::{ip['name']}::="
                ]
        # Object Profile
        for op_id, op_name, metrics in self.db.execute(
            "SELECT id, name, metrics FROM sa_managedobjectprofile"
        ):
            metrics = orjson.loads(metrics)
            for m in metrics:
                if not m.get("threshold_profile"):
                    continue
                thresholds[(str(m["threshold_profile"]), m["metric_type"])] += [
                    f"noc::managedobjectprofile::{op_name}::="
                ]
        # Create Metric Rule and Metric Action
        mas = {}
        mr_bulk = []
        for num, (tp_id, mt) in enumerate(thresholds):
            if tp_id not in thps:
                continue
            tp = thps[tp_id]
            wc = tp.get_window_config()
            if wc and (wc["window_function"], mt) not in mas:
                # Create Metric Action
                mas[(mt, wc["window_function"])] = self.get_metric_action(mt, wc, num=num)
                ma = mas[(mt, wc["window_function"])]
            elif (mt, None) in mas:
                ma = mas[(mt, None)]
            else:
                mas[(mt, None)] = self.get_metric_action(mt, None, num=num)
                ma = mas[(mt, None)]
            ac = tp.get_alarm_config()
            params = {"alarm.activation_level": ac["activation_level"]}
            if "deactivation_level" in ac:
                params["alarm.deactivation_level"] = ac["deactivation_level"]
            if "invert_condition" in ac:
                params["alarm.invert_condition"] = ac["invert_condition"]
            if wc:
                params["activation-window.max_window"] = wc["max_window"]
                params["activation-window.min_window"] = wc["min_window"]
            mr_bulk += [
                InsertOne(
                    {
                        "_id": bson.ObjectId(),
                        "name": f"Migrate threshold profile {tp_id} for Metric Type {mt}",
                        "is_active": False,
                        "match": [
                            {"labels": [ll], "exclude_labels": []} for ll in thresholds[(tp_id, mt)]
                        ],
                        "actions": [
                            {
                                "metric_action": ma["_id"],
                                "is_active": True,
                                "metric_action_params": params,
                            }
                        ],
                    }
                )
            ]
        if mr_bulk:
            self.mongo_db["metricrules"].bulk_write(mr_bulk)
        if mas:
            self.mongo_db["metricactions"].bulk_write([InsertOne(m) for m in mas.values()])
