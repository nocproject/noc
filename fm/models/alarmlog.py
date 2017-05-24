# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlarmLog model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
import noc.lib.nosql as nosql


class AlarmLog(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    timestamp = nosql.DateTimeField()
    from_status = nosql.StringField(
        max_length=1, regex=r"^[AC]$", required=True)
    to_status = nosql.StringField(
        max_length=1, regex=r"^[AC]$", required=True)
    message = nosql.StringField()

    def __unicode__(self):
        return u"%s [%s -> %s]: %s" % (
            self.timestamp, self.from_status,
            self.to_status, self.message)
