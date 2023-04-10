# ---------------------------------------------------------------------
# RCACondition
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from bson import ObjectId


class RCACondition(object):
    def __init__(self, alarm_class, condition):
        self.name = f"{alarm_class.name}::{condition.name}"
        self.window = condition.window
        self.root = condition.root
        self.same_object = False
        # Build condition expression
        self.condition = compile(condition.condition, "<string>", "eval")
        # Build match condition expression
        x = [
            f"'alarm_class': ObjectId('{self.root.id}')",
            f"'timestamp__gte': alarm.timestamp - datetime.timedelta(seconds={self.window})",
            f"'timestamp__lte': alarm.timestamp + datetime.timedelta(seconds={self.window})",
        ]
        if self.root.id == alarm_class.id:
            x += ["'id__ne': alarm.id"]
        for k, v in condition.match_condition.items():
            if k == "managed_object" and v == "alarm.managed_object.id":
                self.same_object = True
            x += [f"'{k}': {v}"]
        self.match_condition = compile("{%s}" % ", ".join(x), "<string>", "eval")
        # Build reverse match condition expression
        x = [
            f"'alarm_class': ObjectId('{alarm_class.id}')",
            "'root__exists': False",
            f"'timestamp__gte': alarm.timestamp - datetime.timedelta(seconds={self.window})",
            f"'timestamp__lte': alarm.timestamp + datetime.timedelta(seconds={self.window})",
        ]
        if self.root.id == alarm_class.id:
            x += ["'id__ne': alarm.id"]
        if self.same_object:
            x += ["'managed_object': alarm.managed_object"]
        self.reverse_match_condition = compile("{%s}" % ", ".join(x), "<string>", "eval")

    def __str__(self):
        return self.name

    def get_context(self, alarm):
        return {"alarm": alarm, "datetime": datetime, "ObjectId": ObjectId}

    def check_condition(self, alarm):
        return eval(self.condition, {}, self.get_context(alarm))

    def get_match_condition(self, alarm, **kwargs):
        r = eval(self.match_condition, {}, self.get_context(alarm))
        if kwargs:
            r.update(kwargs)
        return r

    def get_reverse_match_condition(self, alarm):
        return eval(self.reverse_match_condition, {}, self.get_context(alarm))
