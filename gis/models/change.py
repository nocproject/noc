# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Object changes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
from mongoengine.document import Document

# NOC models
from noc.core.mongo.fields import PlainReferenceField
from .normativedocument import NormativeDocument


class Change(Document):
    meta = {"collection": "noc.changes", "strict": False, "auto_create_index": False}
    document = PlainReferenceField(NormativeDocument)
