# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Layer Settings
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
# Third-party modules
=======
##----------------------------------------------------------------------
## Layer Settings
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from mongoengine.document import Document
from mongoengine.fields import ObjectIdField, IntField, BooleanField


class LayerUserSettings(Document):
    meta = {
        "collection": "noc.layerusersettings",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }
    # User Id
    user = IntField()
    # Layer Id
    layer = ObjectIdField()
    # Visibility
    is_visible = BooleanField(default=True)

    @classmethod
    def is_visible_by_user(cls, user, layer):
        s = LayerUserSettings.objects.filter(user=user.id, layer=layer.id).first()
        if s:
            return s.is_visible
        else:
            return True

    @classmethod
    def set_layer_visibility(cls, user, layer, status):
        s = LayerUserSettings.objects.filter(user=user.id, layer=layer.id).first()
        if not s:
            s = LayerUserSettings(user=user.id, layer=layer.id)
        s.is_visible = status
        s.save()
