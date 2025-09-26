# ----------------------------------------------------------------------
# Migrate SLAProfile threshold profiles
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
import operator

# Third-party modules
import bson
import cachetools

# NOC modules
from noc.core.mongo.connection import get_db
from noc.core.migration.base import BaseMigration

SAVE_FIELDS = {"_id", "metric_type", "enable_periodic", "enable_box", "is_stored"}


class Migration(BaseMigration):
    _ac_cache = cachetools.TTLCache(maxsize=5, ttl=60)

    def migrate(self):
        current = itertools.count()
        db = self.mongo_db
        # Migrate profiles
        p_coll = db["noc.sla_profiles"]
        tp_coll = db["thresholdprofiles"]
        for doc in p_coll.find():
            metrics = doc.get("metrics") or []
            changed = [m for m in metrics if self.has_thresholds(m)]
            if not changed and metrics:
                for metric in metrics:
                    for f in set(metric) - SAVE_FIELDS:
                        del metric[f]
            elif not changed:
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
                tp["name"] = "sp-%05d-%03d" % (next(current), n)
                tp["description"] = "Migrated for SLA profile '%s' metric '%s'" % (
                    doc["name"],
                    metric["metric_type"],
                )
                tp["window_type"] = metric.get("window_type")
                tp["window"] = metric.get("window")
                tp["window_function"] = metric.get("window_function")
                tp["window_config"] = metric.get("window_config")
                # Build thresholds
                tp["thresholds"] = []
                if metric.get("high_error", False):
                    tp["thresholds"] += [
                        {
                            "op": ">=",
                            "value": metric["high_error"],
                            "clear_op": "<",
                            "clear_value": metric["high_error"],
                            "alarm_class": self.get_alarm_class_id("NOC | PM | High Error"),
                        }
                    ]
                if metric.get("low_error", False):
                    tp["thresholds"] += [
                        {
                            "op": "<=",
                            "value": metric["low_error"],
                            "clear_op": ">",
                            "clear_value": metric["low_error"],
                            "alarm_class": self.get_alarm_class_id("NOC | PM | Low Error"),
                        }
                    ]
                if metric.get("low_warn", False):
                    tp["thresholds"] += [
                        {
                            "op": "<=",
                            "value": metric["low_warn"],
                            "clear_op": ">",
                            "clear_value": metric["low_warn"],
                            "alarm_class": self.get_alarm_class_id("NOC | PM | Low Warning"),
                        }
                    ]
                if metric.get("high_warn", False):
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
                metric["threshold_profile"] = tp_id
            # Store back
            p_coll.update_one({"_id": doc.pop("_id")}, {"$set": doc})

    @staticmethod
    def has_thresholds(metric):
        return (
            metric.get("low_error", False)
            or metric.get("low_warn", False)
            or metric.get("high_warn", False)
            or metric.get("high_error", False)
            or metric.get("threshold_profile")
        )

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_ac_cache"))
    def get_alarm_class_id(cls, name):
        db = get_db()
        ac_coll = db["noc.alarmclasses"]
        return ac_coll.find_one({"name": name}, {"_id": 1})["_id"]
