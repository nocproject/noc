# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.AOS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from .oidrules.slot import SlotRule


class Script(GetMetricsScript):
    name = "Alcatel.AOS.get_metrics"

    OID_RULES = [SlotRule]
