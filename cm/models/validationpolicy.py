# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Validation Policy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Mongoengine modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import EmbeddedDocumentField, StringField, BooleanField, ListField, ReferenceField
# NOC modules
=======
##----------------------------------------------------------------------
## Validation Policy
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Mongoengine modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import EmbeddedDocumentField, StringField, BooleanField, ListField, ReferenceField
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from validationrule import ValidationRule


class RuleItem(EmbeddedDocument):
    rule = ReferenceField(ValidationRule)
    is_active = BooleanField(default=True)

    def __unicode__(self):
        return self.rule.name


class ValidationPolicy(Document):
    meta = {
<<<<<<< HEAD
        "collection": "noc.validationpolicy",
        "strict": False,
        "auto_create_index": False
=======
        "collection": "noc.validationpolicy"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    rules = ListField(EmbeddedDocumentField(RuleItem))

    def __unicode__(self):
        return self.name
