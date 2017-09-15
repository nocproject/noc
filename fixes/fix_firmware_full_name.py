# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Fix Firmware.full_name
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.inv.models.firmware import Firmware


def fix():
    for fw in Firmware.objects.all():
        fw.save()
