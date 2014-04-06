# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Object changes
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (ObjectIdField, IntField, BooleanField,
                                ListField, EmbeddedDocumentField)
## NOC models
from normativedocument import NormativeDocument
from noc.lib.nosql import PlainReferenceField


class Change(Document):
    meta = {
        "collection": "noc.changes",
        "allow_inheritance": False
    }
    document = PlainReferenceField(NormativeDocument)
