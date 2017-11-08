# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Object changes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
# NOC models
from normativedocument import NormativeDocument
from noc.lib.nosql import PlainReferenceField


class Change(Document):
    meta = {
        "collection": "noc.changes",
        "strict": False,
        "auto_create_index": False
    }
    document = PlainReferenceField(NormativeDocument)
