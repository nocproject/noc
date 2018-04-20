# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmClassJob model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.lib.nosql as nosql


class AlarmClassJob(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    # Job name (fm/correlator/jobs/<name>.py)
    job = nosql.StringField(required=True)
    # Start job after *delay* seconds after alarm risen
    # delay = nosql.IntField(required=False, default=0)
    # Restart job every *interval* seconds
    interval = nosql.IntField(required=False, default=0)
    # Job parameters: name -> expression
    vars = nosql.DictField(required=True)

    def __unicode__(self):
        return self.job

    def __eq__(self, other):
        return (
            self.job == other.job and
            self.interval == other.interval and
            self.vars == other.vars
        )
