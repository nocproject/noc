<<<<<<< HEAD
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ModelMapping model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
=======
## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ModelMapping model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField)
from noc.inv.models.objectmodel import ObjectModel
from noc.lib.nosql import PlainReferenceField


class ModelMapping(Document):
    meta = {
        "collection": "noc.modelmappings",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }

    # Vendor, as returned by get_inventory
    vendor = StringField()
    # Part number, as returned by get_inventory
    part_no = StringField()
    # Serial number ranges, if applicable
    from_serial = StringField()
    to_serial = StringField()
    #
    model = PlainReferenceField(ObjectModel)
    #
    is_active = BooleanField(default=True)
<<<<<<< HEAD
    description = StringField(required=False)
=======
    description = StringField(required=False)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
