# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlarmLog model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six

# NOC modules
import noc.lib.nosql as nosql


@six.python_2_unicode_compatible
class AlarmLog(nosql.EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    timestamp = nosql.DateTimeField()
    from_status = nosql.StringField(max_length=1, regex=r"^[AC]$", required=True)
    to_status = nosql.StringField(max_length=1, regex=r"^[AC]$", required=True)
    message = nosql.StringField()

    def __str__(self):
        return "%s [%s -> %s]: %s" % (
            self.timestamp,
            self.from_status,
            self.to_status,
            self.message,
        )
