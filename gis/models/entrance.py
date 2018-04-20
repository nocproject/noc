# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Entrance object
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
=======
##----------------------------------------------------------------------
## Entrance object
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, IntField, BooleanField


class Entrance(EmbeddedDocument):
    meta = {
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }
    number = StringField()
    # Floors
    first_floor = IntField()
    last_floor = IntField()
    #
    first_home = StringField()
    last_home = StringField()
    # @todo: Managing company

    def __unicode__(self):
<<<<<<< HEAD
        return self.number
=======
        return self.number
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
