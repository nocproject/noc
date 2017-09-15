# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Fix platform.full_name
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.inv.models.platform import Platform


def fix():
    for p in Platform.objects.all():
        p.save()
