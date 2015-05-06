# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Validation Rule
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField, DictField,
                                ListField, EmbeddedDocumentField)
from mongoengine.signals import pre_delete
## NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.lib.nosql import ForeignKeyField
from noc.lib.solutions import get_solution

logger = logging.getLogger(__name__)

A_DISABLE = ""
A_INCLUDE = "I"
A_EXCLUDE = "X"

ACTIONS = [
    (A_DISABLE, "Disable"),
    (A_INCLUDE, "Include"),
    (A_EXCLUDE, "Exclude")
]


class SelectorItem(EmbeddedDocument):
    selector = ForeignKeyField(ManagedObjectSelector)
    action = StringField(choices=ACTIONS)

    def __unicode__(self):
        return u"%s: %s" % (self.action, self.selector.name)


class ObjectItem(EmbeddedDocument):
    object = ForeignKeyField(ManagedObject)
    action = StringField(choices=ACTIONS)

    def __unicode__(self):
        return u"%s: %s" % (self.action, self.object.name)


class ValidationRule(Document):
    meta = {
        "collection": "noc.validationrules"
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    selectors_list = ListField(EmbeddedDocumentField(SelectorItem))
    objects_list = ListField(EmbeddedDocumentField(ObjectItem))
    handler = StringField()
    config = DictField()

    def __unicode__(self):
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
            return get_solution(self.handler)
        else:
            return None

    @classmethod
    def on_delete(cls, sender, document, **kwargs):
        from validationpolicy import ValidationPolicy
        logger.info("Deleting rule %s", document.name)
        for vp in ValidationPolicy.objects.filter(rules__rule=document):
            logger.info("Removing rule %s from policy %s",
                        document.name, vp.name)
            vp.rules = [r for r in vp.rules if r.rule.id != document.id]
            vp.save()


pre_delete.connect(ValidationRule.on_delete, sender=ValidationRule)
