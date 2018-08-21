# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Set Link.objects
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
# NOC modules
from noc.inv.models.link import Link


def fix():
    for l in Link.objects.filter().timeout(False):
        try:
            l.save()
        except AssertionError:
            print("Assertion Error, check link with id: %s" % l.id)
