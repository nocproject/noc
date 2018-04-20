# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IgnorePattern model
# Propagated to collectors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
=======
##----------------------------------------------------------------------
## IgnorePattern model
## Propagated to collectors
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField


class IgnorePattern(Document):
    meta = {
        "collection": "noc.fm.ignorepatterns",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }

    source = StringField()
    pattern = StringField()
    is_active = BooleanField()
    description = StringField(required=False)

    def __unicode__(self):
        return u"%s: %s" % (self.source, self.pattern)
