# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Set Link.objects
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.inv.models.link import Link


def fix():
    for l in Link.objects.filter(linked_objects__exists=False).timeout(False):
        l.save()
