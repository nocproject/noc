# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Object changes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (ObjectIdField, IntField, BooleanField,
                                ListField, EmbeddedDocumentField)
# NOC models
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from normativedocument import NormativeDocument
from noc.lib.nosql import PlainReferenceField


class Change(Document):
    meta = {
        "collection": "noc.changes",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }
    document = PlainReferenceField(NormativeDocument)
