# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Set Link.objects
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.queryset import Q
# NOC modules
from noc.inv.models.link import Link


def fix():
    for l in Link.objects.filter(
            Q(linked_objects__exists=False) |
            Q(linked_segments__exists=False) |
            Q(type__exists=False)
    ).timeout(False):
        l.save()
