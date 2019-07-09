# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Validation Rule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging

# Third-party modules
import six
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    DictField,
    ListField,
    EmbeddedDocumentField,
)
from mongoengine.signals import pre_delete

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.core.mongo.fields import ForeignKeyField
from noc.core.handler import get_handler

logger = logging.getLogger(__name__)

A_DISABLE = ""
A_INCLUDE = "I"
A_EXCLUDE = "X"

ACTIONS = [(A_DISABLE, "Disable"), (A_INCLUDE, "Include"), (A_EXCLUDE, "Exclude")]


@six.python_2_unicode_compatible
class SelectorItem(EmbeddedDocument):
    selector = ForeignKeyField(ManagedObjectSelector)
    action = StringField(choices=ACTIONS)

    def __str__(self):
        return "%s: %s" % (self.action, self.selector.name)


@six.python_2_unicode_compatible
class ObjectItem(EmbeddedDocument):
    object = ForeignKeyField(ManagedObject)
    action = StringField(choices=ACTIONS)

    def __str__(self):
        return "%s: %s" % (self.action, self.object.name)


@six.python_2_unicode_compatible
class ValidationRule(Document):
    meta = {"collection": "noc.validationrules", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    selectors_list = ListField(EmbeddedDocumentField(SelectorItem))
    objects_list = ListField(EmbeddedDocumentField(ObjectItem))
    handler = StringField()
    config = DictField()

    def __str__(self):
        return self.name

    def is_applicable_for(self, object):
        """
        Check rule is applicable for managed object
        """
        if self.objects_list:
            actions = set(i.action for i in self.objects_list if i.object == object)
            if A_DISABLE not in actions:
                if A_EXCLUDE in actions:
                    return False
                elif A_INCLUDE in actions:
                    return True
        if self.selectors_list:
            actions = set(s.action for s in self.selectors_list if object in s.selector)
            if A_DISABLE not in actions:
                if A_EXCLUDE in actions:
                    return False
                elif A_INCLUDE in actions:
                    return True
        return not self.selectors_list and not self.objects_list

    def get_handler(self):
        if self.handler:
            return get_handler(self.handler)
        else:
            return None

    @classmethod
    def on_delete(cls, sender, document, **kwargs):
        from noc.cm.models.validationpolicy import ValidationPolicy

        logger.info("Deleting rule %s", document.name)
        for vp in ValidationPolicy.objects.filter(rules__rule=document):
            logger.info("Removing rule %s from policy %s", document.name, vp.name)
            vp.rules = [r for r in vp.rules if r.rule.id != document.id]
            vp.save()


pre_delete.connect(ValidationRule.on_delete, sender=ValidationRule)
