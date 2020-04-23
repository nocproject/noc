# ----------------------------------------------------------------------
# Interface Profile dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField


class SubscriberProfile(Dictionary):
    class Meta(object):
        name = "subscriberprofile"
        layout = "flat"

    name = StringField()
    desription = StringField()
    glyph = StringField()
