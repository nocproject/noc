# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Migrate InterfaceProfile threshold profiles
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
# Third-party modules
import bson
from south.db import db
from six.moves.cPickle import loads, dumps, HIGHEST_PROTOCOL
# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        current = itertools.count()
        mdb = get_db()
        # Get alarm classes
        ac_coll = mdb["noc.alarmclasses"]
        ac_he = ac_coll.find_one({"name": "NOC | PM | High Error"}, {"_id": 1})["_id"]
        ac_le = ac_coll.find_one({"name": "NOC | PM | Low Error"}, {"_id": 1})["_id"]
        ac_hw = ac_coll.find_one({"name": "NOC | PM | High Warning"}, {"_id": 1})["_id"]
        ac_lw = ac_coll.find_one({"name": "NOC | PM | Low Warning"}, {"_id": 1})["_id"]
        # Migrate profiles
        tp_coll = mdb["thresholdprofiles"]
        settings = db.execute("SELECT id, name, metrics FROM sa_managedobjectprofile")
        for p_id, name, p_metrics in settings:
            if not p_metrics:
                continue
            metrics = loads(str(p_metrics)) or []
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
                tp["name"] = "op-%05d-%03d" % (next(current), n)
                tp["description"] = "Migrated for interface profile '%s' metric '%s'" % (
                    name,
                    metric["metric_type"]
                )
                tp["window_type"] = metric.get("window_type")
                tp["window"] = metric.get("window")
                tp["window_function"] = metric.get("window_function")
                tp["window_config"] = metric.get("window_config")
                # Build thresholds
                tp["thresholds"] = []
                if metric.get("high_error", False):
                    tp["thresholds"] += [{
                        "op": ">=",
                        "value": metric["high_error"],
                        "clear_op": "<",
                        "clear_value": metric["high_error"],
                        "alarm_class": ac_he
                    }]
                if metric.get("low_error", False):
                    tp["thresholds"] += [{
                        "op": "<=",
                        "value": metric["low_error"],
                        "clear_op": ">",
                        "clear_value": metric["low_error"],
                        "alarm_class": ac_le
                    }]
                if metric.get("low_warn", False):
                    tp["thresholds"] += [{
                        "op": "<=",
                        "value": metric["low_warn"],
                        "clear_op": ">",
                        "clear_value": metric["low_warn"],
                        "alarm_class": ac_lw
                    }]
                if metric.get("high_warn", False):
                    tp["thresholds"] += [{
                        "op": ">=",
                        "value": metric["high_warn"],
                        "clear_op": "<",
                        "clear_value": metric["high_warn"],
                        "alarm_class": ac_hw
                    }]
                # Save profile
                tp_coll.insert_one(tp)
                #
                metric["threshold_profile"] = tp_id
            # Store back
            wb_metrics = dumps(metrics, HIGHEST_PROTOCOL)
            db.execute("UPDATE sa_managedobjectprofile SET metric=%s WHERE id=%s", [wb_metrics, p_id])

    def backwards(self):
        pass

    @staticmethod
    def has_thresholds(metric):
        return (metric.get("low_error", False) or metric.get("low_warn", False) or
                metric.get("high_warn", False) or metric.get("high_error", False) or
                metric.get("threshold_profile"))
