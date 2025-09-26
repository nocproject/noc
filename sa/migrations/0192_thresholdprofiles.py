# ----------------------------------------------------------------------
# Migrate InterfaceProfile threshold profiles
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
import operator
from pickle import loads, dumps, HIGHEST_PROTOCOL

# Third-party modules
import bson
import psycopg2
import cachetools

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.mongo.connection import get_db
from noc.core.comp import smart_bytes


class Migration(BaseMigration):
    _ac_cache = cachetools.TTLCache(maxsize=5, ttl=60)

    def migrate(self):
        # Convert pickled field ty BYTEA
        self.db.execute(
            "ALTER TABLE sa_managedobjectprofile ALTER metrics TYPE BYTEA USING metrics::bytea"
        )
        current = itertools.count()
        mdb = self.mongo_db
        # Migrate profiles
        tp_coll = mdb["thresholdprofiles"]
        settings = self.db.execute("SELECT id, name, metrics FROM sa_managedobjectprofile")
        for p_id, name, p_metrics in settings:
            if not p_metrics:
                continue
            metrics = loads(smart_bytes(p_metrics)) or []
            changed = [m for m in metrics if self.has_thresholds(m)]
            if not changed:
                continue
            for n, metric in enumerate(changed):
                tp_id = bson.ObjectId()
                if metric.get("threshold_profile"):
                    # Extend existent threshold profile
                    tp = tp_coll.find_one({"_id": metric["threshold_profile"]})
                    assert tp, "Broken threshold profile"
                    tp["_id"] = tp_id
                else:
                    tp = {"_id": tp_id}
                # Fill profile
                tp["name"] = "op14-%05d-%03d" % (next(current), n)
                tp["description"] = "Migrated for interface profile '%s' metric '%s'" % (
                    name,
                    metric["metric_type"],
                )
                tp["window_type"] = metric.get("window_type")
                tp["window"] = metric.get("window")
                tp["window_function"] = metric.get("window_function")
                tp["window_config"] = metric.get("window_config")
                # Build thresholds
                tp["thresholds"] = []
                if metric.get("high_error", False) or metric.get("high_error", None) == 0:
                    tp["thresholds"] += [
                        {
                            "op": ">=",
                            "value": metric["high_error"],
                            "clear_op": "<",
                            "clear_value": metric["high_error"],
                            "alarm_class": self.get_alarm_class_id("NOC | PM | High Error"),
                        }
                    ]
                if metric.get("low_error", False) or metric.get("low_error", None) == 0:
                    tp["thresholds"] += [
                        {
                            "op": "<=",
                            "value": metric["low_error"],
                            "clear_op": ">",
                            "clear_value": metric["low_error"],
                            "alarm_class": self.get_alarm_class_id("NOC | PM | Low Error"),
                        }
                    ]
                if metric.get("low_warn", False) or metric.get("low_warn", None) == 0:
                    tp["thresholds"] += [
                        {
                            "op": "<=",
                            "value": metric["low_warn"],
                            "clear_op": ">",
                            "clear_value": metric["low_warn"],
                            "alarm_class": self.get_alarm_class_id("NOC | PM | Low Warning"),
                        }
                    ]
                if metric.get("high_warn", False) or metric.get("high_warn", None) == 0:
                    tp["thresholds"] += [
                        {
                            "op": ">=",
                            "value": metric["high_warn"],
                            "clear_op": "<",
                            "clear_value": metric["high_warn"],
                            "alarm_class": self.get_alarm_class_id("NOC | PM | High Warning"),
                        }
                    ]
                # Save profile
                tp_coll.insert_one(tp)
                metric["threshold_profile"] = str(tp_id)
            # Store back
            wb_metrics = psycopg2.Binary(dumps(metrics, HIGHEST_PROTOCOL))
            self.db.execute(
                "UPDATE sa_managedobjectprofile SET metrics=%s WHERE id=%s", [wb_metrics, p_id]
            )

    @staticmethod
    def has_thresholds(metric):
        return (
            metric.get("low_error", False)
            or metric.get("low_warn", False)
            or metric.get("high_warn", False)
            or metric.get("high_error", False)
            or metric.get("low_error", None) == 0
            or metric.get("low_warn", None) == 0
            or metric.get("high_warn", None) == 0
            or metric.get("high_error", None) == 0
            or metric.get("threshold_profile")
        )

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_ac_cache"))
    def get_alarm_class_id(cls, name):
        db = get_db()
        ac_coll = db["noc.alarmclasses"]
        return ac_coll.find_one({"name": name}, {"_id": 1})["_id"]
