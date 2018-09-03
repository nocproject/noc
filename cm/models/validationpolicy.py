# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Validation Policy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import EmbeddedDocumentField, StringField, BooleanField, ListField, ReferenceField
# NOC modules
from .validationrule import ValidationRule


class RuleItem(EmbeddedDocument):
    rule = ReferenceField(ValidationRule)
    is_active = BooleanField(default=True)

    def __unicode__(self):
        return self.rule.name


class ValidationPolicy(Document):
    meta = {
        "collection": "noc.validationpolicy",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    rules = ListField(EmbeddedDocumentField(RuleItem))

    def __unicode__(self):
        return self.name
