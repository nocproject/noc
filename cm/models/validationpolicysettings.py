# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Policy Settings
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, ReferenceField, ListField,
                                EmbeddedDocumentField, BooleanField)
# NOC modules
=======
##----------------------------------------------------------------------
## Policy Settings
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, ReferenceField, ListField,
                                EmbeddedDocumentField, BooleanField)
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from validationpolicy import ValidationPolicy


class ValidationPolicyItem(EmbeddedDocument):
    policy = ReferenceField(ValidationPolicy)
    is_active = BooleanField(default=True)

    def __unicode__(self):
        return self.policy.name


class ValidationPolicySettings(Document):
    meta = {
        "collection": "noc.validationpolicysettings",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "indexes": [("model_id", "object_id")]
    }
    model_id = StringField()
    object_id = StringField()
    policies = ListField(EmbeddedDocumentField(ValidationPolicyItem))

    def __unicode__(self):
        return u"%s: %s" % (self.model_id, self.object_id)
