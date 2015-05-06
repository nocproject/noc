# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Normative Document object
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, DateField, StringField)
from noc.lib.nosql import PlainReferenceField


class NormativeDocument(Document):
    meta = {
        "collection": "noc.normative_documents",
        "allow_inheritance": False
    }
    name = StringField()
    doc_date = DateField()
    number = StringField()
    # @todo: Type
