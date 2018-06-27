# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Rebuild datastreams from scratch
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.models.managedobject import ManagedObject


def fix():
    for mo in ManagedObject.objects.all():
        mo.save()  # Force datastream rebuild
