# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlarmRootCauseCondition model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
import noc.lib.nosql as nosql


class AlarmRootCauseCondition(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }

    name = nosql.StringField(required=True)
    root = nosql.PlainReferenceField("fm.AlarmClass")
    window = nosql.IntField(required=True)
    condition = nosql.StringField(default="True")
    match_condition = nosql.DictField(required=True)

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name and
            (
                (self.root is None and other.root is None) or
                (
                    self.root and other.root and
                    self.root.id == other.root.id
                )
            ) and
            self.window == other.window and
            self.condition == other.condition and
            self.match_condition == other.match_condition
        )
