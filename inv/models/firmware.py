# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Firmware
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014=6 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField


class Firmware(Document):
    meta = {
        "collection": "noc.firmware",
        "strict": False,
    }
    # Firmware name
    name = StringField(unique=True)
    #
    vendor = StringField()
    version = StringField()
    description = StringField()
    download_url = StringField()

    def __unicode__(self):
        return self.name
