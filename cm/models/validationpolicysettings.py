# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Policy Settings
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ReferenceField,
    ListField,
    EmbeddedDocumentField,
    BooleanField,
)

# NOC modules
from .validationpolicy import ValidationPolicy


@six.python_2_unicode_compatible
class ValidationPolicyItem(EmbeddedDocument):
    policy = ReferenceField(ValidationPolicy)
    is_active = BooleanField(default=True)

    def __str__(self):
        return self.policy.name


@six.python_2_unicode_compatible
class ValidationPolicySettings(Document):
    meta = {
        "collection": "noc.validationpolicysettings",
        "strict": False,
        "auto_create_index": False,
        "indexes": [("model_id", "object_id")],
    }
    model_id = StringField()
    object_id = StringField()
    policies = ListField(EmbeddedDocumentField(ValidationPolicyItem))

    def __str__(self):
        return "%s: %s" % (self.model_id, self.object_id)
