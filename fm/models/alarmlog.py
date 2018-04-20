# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# AlarmLog model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## AlarmLog model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import noc.lib.nosql as nosql


class AlarmLog(nosql.EmbeddedDocument):
    meta = {
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
